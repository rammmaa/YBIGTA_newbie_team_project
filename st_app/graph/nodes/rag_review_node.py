import os
import sys
from typing import Dict, Any
from langchain_core.messages import AIMessage
from langchain_upstage import ChatUpstage
from langchain_core.prompts import ChatPromptTemplate
from st_app.utils.state import GraphState

# st_app 디렉토리를 Python 경로에 추가
st_app_path = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
sys.path.append(st_app_path)

from st_app.rag.retriever import get_retriever
from st_app.rag.llm import get_rag_chain

# LLM 초기화
chat_model = ChatUpstage(model="solar-pro2")

# RAG 리뷰 프롬프트
RAG_REVIEW_PROMPT = ChatPromptTemplate.from_template("""
당신은 연돈 식당에 대한 리뷰 정보를 제공하는 전문 어시스턴트입니다.

다음은 연돈에 대한 실제 고객 리뷰들입니다:

**검색된 리뷰 내용:**
{retrieved_reviews}

사용자의 질문에 대해 위 리뷰 정보를 바탕으로 친근하고 도움이 되는 답변을 제공해주세요.
리뷰 내용을 인용하거나 요약하여 답변해주세요.
답변은 자연스럽고 대화체로 작성해주세요.

만약 검색된 리뷰가 충분하지 않다면, 그 점을 언급하고 가능한 범위 내에서 답변해주세요.

사용자 질문: {user_message}

답변:
""")

def rag_review_node(state: GraphState) -> Dict[str, Any]:
    """
    RAG를 사용하여 리뷰 정보를 바탕으로 답변하는 노드
    
    Args:
        state: 현재 그래프 상태
        
    Returns:
        업데이트된 상태
    """
    # 마지막 사용자 메시지 가져오기
    last_message = state["messages"][-1]
    user_message = last_message.content
    
    try:
        # RAG 체인 초기화
        retriever = get_retriever()
        rag_chain = get_rag_chain(retriever)
        
        # RAG를 통한 응답 생성
        response = rag_chain.invoke(user_message)
        
        # 검색된 리뷰 내용 가져오기 (retriever에서 직접 가져오기)
        retrieved_docs = retriever.get_relevant_documents(user_message)
        retrieved_reviews = [doc.page_content for doc in retrieved_docs]
        
    except Exception as e:
        # RAG 실패 시 대체 응답
        response_content = f"죄송합니다. 리뷰 정보를 가져오는 중 오류가 발생했습니다: {str(e)}"
        retrieved_reviews = []
        
        # 프롬프트 생성 및 LLM 호출
        prompt = RAG_REVIEW_PROMPT.format(
            retrieved_reviews="리뷰 정보를 가져올 수 없습니다.",
            user_message=user_message
        )
        response = chat_model.invoke(prompt)
    
    # AI 메시지 생성
    ai_message = AIMessage(content=response.content if hasattr(response, 'content') else str(response))
    
    return {
        **state,
        "messages": state["messages"] + [ai_message],
        "current_node": "chat",  # 다시 채팅 노드로 복귀
        "retrieved_reviews": retrieved_reviews,
        "routing_decision": "end"
    }
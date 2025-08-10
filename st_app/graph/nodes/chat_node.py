from typing import Dict, Any
from langchain_core.messages import HumanMessage, AIMessage
from langchain_upstage import ChatUpstage
from langchain_core.prompts import ChatPromptTemplate
from st_app.utils.state import GraphState

# LLM 초기화
chat_model = ChatUpstage(model="solar-pro2")

# 기본 대화 프롬프트
CHAT_PROMPT = ChatPromptTemplate.from_template("""
당신은 친근하고 도움이 되는 AI 어시스턴트입니다. 
사용자와 자연스럽게 대화하며, 연돈 식당에 대한 질문이 있으면 적절히 답변해주세요.

만약 사용자가 연돈에 대한 구체적인 정보(메뉴, 위치, 영업시간 등)를 원한다면, 
"SUBJECT_INFO"라고 답변하세요.

만약 사용자가 연돈에 대한 리뷰나 후기를 원한다면, 
"RAG_REVIEW"라고 답변하세요.

그 외의 일반적인 대화는 자연스럽게 진행하세요.

사용자 메시지: {user_message}

답변:
""")

def chat_node(state: GraphState) -> Dict[str, Any]:
    """
    기본 대화를 수행하는 노드
    
    Args:
        state: 현재 그래프 상태
        
    Returns:
        업데이트된 상태
    """
    # 마지막 사용자 메시지 가져오기
    last_message = state["messages"][-1]
    user_message = last_message.content
    
    # 프롬프트 생성 및 LLM 호출
    prompt = CHAT_PROMPT.format(user_message=user_message)
    response = chat_model.invoke(prompt)
    
    # 응답 내용 확인
    response_content = response.content.strip()
    
    # 라우팅 결정
    if "SUBJECT_INFO" in response_content:
        # 주제 정보 노드로 라우팅
        return {
            **state,
            "current_node": "subject_info",
            "routing_decision": "subject_info"
        }
    elif "RAG_REVIEW" in response_content:
        # RAG 리뷰 노드로 라우팅
        return {
            **state,
            "current_node": "rag_review", 
            "routing_decision": "rag_review"
        }
    else:
        # 일반 대화 계속
        ai_message = AIMessage(content=response_content)
        return {
            **state,
            "messages": state["messages"] + [ai_message],
            "current_node": "chat",
            "routing_decision": "continue_chat"
        }

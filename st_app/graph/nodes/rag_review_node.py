from typing import Dict, Any, List
import os
from langchain_core.messages import AIMessage, BaseMessage
from langchain_upstage import ChatUpstage

from st_app.utils.state import GraphState
from st_app.rag.retriever import ReviewRetriever
from st_app.rag.llm import get_rag_chain
from st_app.rag.prompt import CHAT_PROMPT  
from dotenv import load_dotenv

load_dotenv()

chat_model = ChatUpstage(
    model=os.getenv("UPSTAGE_CHAT_MODEL", "solar-pro2"),
    api_key=os.getenv("UPSTAGE_API_KEY"),
    temperature=0.3,
    max_tokens=768,
)

def rag_review_node(state: GraphState) -> Dict[str, Any]:
    """
    리뷰 RAG 노드:
    - retriever로 컨텍스트 검색
    - get_rag_chain(내부 RAG_PROMPT)으로 답변 생성
    - 예외 시 CHAT_PROMPT로 안내 후 Chat으로 복귀
    Args:
        state: 현재 그래프 상태
    Returns:
        Dict[str, Any]: 업데이트된 상태
    """
    last_message: BaseMessage = state["messages"][-1]
    user_message = getattr(last_message, "content", "")

    try:
        # 1) 검색기 & 체인
        retriever = ReviewRetriever(top_k=3)
        run_rag = get_rag_chain(retriever)  # 내부에서 RAG_PROMPT 사용

        # 2) 실행
        response_text = run_rag(user_message)

        # 3) 검색 결과 원문 저장(선택)
        hits = retriever.retrieve(user_message)
        retrieved_reviews: List[str] = [h["text"] for h in hits]

    except Exception as e:
        # 폴백: CHAT_PROMPT로 상황 안내
        retrieved_reviews = []
        msgs = CHAT_PROMPT.format_messages(
            user_input=f"리뷰 컨텍스트를 불러오지 못했어요. 질문: {user_message}\n"
                       f"가능한 범위에서 간단히 도와줘. (오류: {e})"
        )
        resp = chat_model.invoke(msgs)
        response_text = resp.content if hasattr(resp, "content") else str(resp)

    ai_message = AIMessage(content=response_text)
    return {
        **state,
        "messages": state["messages"] + [ai_message],
        "current_node": "chat",          # 처리 후 chat로 복귀 (다음 분기는 router가 판단)
        "retrieved_reviews": retrieved_reviews,
        "routing_decision": None,
    }

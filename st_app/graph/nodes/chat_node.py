from typing import Dict, Any, cast
from langchain_core.messages import AIMessage, BaseMessage
from langchain_upstage import ChatUpstage
from st_app.utils.state import GraphState
from st_app.rag.llm import get_chat_llm
from st_app.rag.prompt import CHAT_PROMPT

def chat_node(state: GraphState) -> Dict[str, Any]:
    """
    기본 대화를 수행하는 노드
    
    Args:
        state: 현재 그래프 상태
        
    Returns:
        업데이트된 상태
    """
    # 마지막 사용자 메시지
    last: BaseMessage = state["messages"][-1]
    user_text = getattr(last, "content", "")

    # Upstage LLM 호출
    llm = get_chat_llm()
    msgs = CHAT_PROMPT.format_messages(user_message=user_text)
    resp = llm.invoke(msgs)
    answer = getattr(resp, "content", str(resp)).strip()

    # 답변 메시지 추가
    ai_msg = AIMessage(content=answer)
    return {
        **state,
        "messages": cast(list, state["messages"]) + [ai_msg],
        "current_node": "chat",          # 처리 후 기본 채팅 상태 유지
        "routing_decision": None,        # 실제 라우팅은 router가 결정
    }
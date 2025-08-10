# st_app/graph/router.py
from typing import Literal, List
from langgraph.graph import StateGraph, END
from langchain_core.messages import BaseMessage
from st_app.utils.state import GraphState
from st_app.graph.nodes.chat_node import chat_node
from st_app.graph.nodes.subject_info_node import subject_info_node
from st_app.graph.nodes.rag_review_node import rag_review_node
from st_app.rag.llm import get_chat_llm

ROUTER_SYSTEM = (
    "너는 사용자의 마지막 메시지를 보고 다음 중 하나의 라벨만 출력한다.\n"
    "- chat: 일반 대화/스몰토크/간단한 질문\n"
    "- subject_info: 주소/영업시간/설명/메뉴 등 사실 정보 질의\n"
    "- rag_review: 리뷰/후기/웨이팅/가격 체감 등 리뷰 근거가 필요한 질의\n"
    "설명 없이 소문자 라벨만 한 단어로 출력."
)

def _classify_intent(state: GraphState) -> Literal["chat","subject_info","rag_review"]:
    """사용자의 의도를 분류합니다.
    Args:
        state (GraphState): 현재 그래프 상태

    Returns:
        Literal["chat","subject_info","rag_review"]: 사용자의 의도에 따라 'chat', 'subject_info', 'rag_review' 중 하나의 라벨을 반환합니다.
    """
    # Upstage LLM을 사용하여 사용자 메시지 분류
    llm = get_chat_llm(temperature=0.0)
    user_last = getattr(state["messages"][-1], "content", "")
    resp = llm.invoke([
        {"role":"system","content":ROUTER_SYSTEM},
        {"role":"user","content":user_last},
    ])
    
    # 응답에서 라벨 추출
    label = (getattr(resp, "content", str(resp)) or "").strip().lower()
    if label not in {"chat","subject_info","rag_review"}:
        label = "chat"
    state["routing_decision"] = label
    return label

def _route_node(state: GraphState) -> GraphState:
    # 상태를 그대로 넘기는 ‘빈’ 노드 (분기만 수행)
    return state

def create_router_graph() -> StateGraph:
    """라우팅 그래프를 생성합니다.

    Returns:
        StateGraph: 생성된 라우팅 그래프
    """
    g = StateGraph(GraphState)

    # 노드 등록
    g.add_node("route", _route_node)   
    g.add_node("chat", chat_node)
    g.add_node("subject_info", subject_info_node)
    g.add_node("rag_review", rag_review_node)

    # 시작점: route
    g.set_entry_point("route")

    # route → (chat | subject_info | rag_review)
    g.add_conditional_edges(
        "route",
        _classify_intent,
        {"chat":"chat","subject_info":"subject_info","rag_review":"rag_review"},
    )

    # 각 노드 처리 후 → 다시 route (다음 턴 분기)
    g.add_edge("chat", END)
    g.add_edge("subject_info", END)
    g.add_edge("rag_review", END)

    return g.compile()

def create_initial_state(messages: List[BaseMessage]) -> GraphState:
    """초기 상태를 생성합니다.
    Args:
        messages (List[BaseMessage]): 초기 메시지 목록  
    Returns:
        GraphState: 초기 상태 객체
    """
    return GraphState(
        messages=messages,
        current_node="route",
        subject_info=None,
        retrieved_reviews=None,
        routing_decision=None,
    )

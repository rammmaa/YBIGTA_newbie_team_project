from typing import Dict, Any, Literal
from langchain_core.messages import BaseMessage
from langgraph.graph import StateGraph, END
from st_app.utils.state import GraphState
from st_app.graph.nodes.chat_node import chat_node
from st_app.graph.nodes.subject_info_node import subject_info_node
from st_app.graph.nodes.rag_review_node import rag_review_node

def create_router_graph():
    """
    LangGraph를 사용한 조건부 라우팅 그래프를 생성합니다.
    
    Returns:
        StateGraph: 라우팅 그래프
    """
    
    # 상태 그래프 생성
    workflow = StateGraph(GraphState)
    
    # 노드 추가
    workflow.add_node("chat", chat_node)
    workflow.add_node("subject_info", subject_info_node)
    workflow.add_node("rag_review", rag_review_node)
    
    # 시작 노드 설정
    workflow.set_entry_point("chat")
    
    # 조건부 라우팅 함수
    def route_decision(state: GraphState) -> Literal["chat", "subject_info", "rag_review", "__end__"]:
        """
        현재 상태를 기반으로 다음 노드를 결정합니다.
        
        Args:
            state: 현재 그래프 상태
            
        Returns:
            다음 실행할 노드 이름
        """
        routing_decision = state.get("routing_decision", "continue_chat")
        
        if routing_decision == "subject_info":
            return "subject_info"
        elif routing_decision == "rag_review":
            return "rag_review"
        elif routing_decision == "return_to_chat":
            return "chat"
        else:
            return "chat"
    
    # 조건부 엣지 추가
    workflow.add_conditional_edges(
        "chat",
        route_decision,
        {
            "chat": "chat",
            "subject_info": "subject_info", 
            "rag_review": "rag_review"
        }
    )
    
    # subject_info와 rag_review 노드에서 chat으로 복귀
    workflow.add_edge("subject_info", "chat")
    workflow.add_edge("rag_review", "chat")
    
    # 그래프 컴파일
    app = workflow.compile()
    
    return app

def create_initial_state(messages: list[BaseMessage]) -> GraphState:
    """
    초기 상태를 생성합니다.
    
    Args:
        messages: 초기 메시지 리스트
        
    Returns:
        초기 그래프 상태
    """
    return GraphState(
        messages=messages,
        current_node="chat",
        subject_info=None,
        retrieved_reviews=None,
        routing_decision=None
    )

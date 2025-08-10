from typing import TypedDict, List, Optional
from langchain_core.messages import BaseMessage

class GraphState(TypedDict):
    """
    LangGraph에서 사용하는 상태 클래스
    
    Attributes:
        messages: 대화 메시지 히스토리
        current_node: 현재 실행 중인 노드 이름
        subject_info: 리뷰 대상 정보 (필요시)
        retrieved_reviews: 검색된 리뷰 내용 (필요시)
        routing_decision: 라우팅 결정 결과
    """
    messages: List[BaseMessage]
    current_node: str
    subject_info: Optional[dict]
    retrieved_reviews: Optional[List[str]]
    routing_decision: Optional[str]
    
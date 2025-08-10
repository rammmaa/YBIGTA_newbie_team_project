import json
import os
from typing import Dict, Any
from langchain_core.messages import AIMessage, BaseMessage
from st_app.rag.llm import get_chat_llm
from st_app.utils.state import GraphState
from st_app.rag.prompt import SUBJECT_INFO_PROMPT

def load_subject_info() -> Dict[str, Any]:
    """
    연돈 식당 정보를 로드합니다.
    Returns:
        Dict[str, Any]: 식당 정보 딕셔너리
    """
    try:
        info_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
            "db", "subject_information", "subjects.json"
        )
        with open(info_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        return {
            "이름": "연돈",
            "위치": "제주특별자치도 서귀포시",
            "종류": "돈까스 전문식당",
            "영업 시간": "12:00-21:00",
            "전화번호": "0507-1386-7060",
            "메뉴": ["등심까스", "안심까스", "치즈까스", "하이라이스", "카레"]
        }


def subject_info_node(state: GraphState) -> Dict[str, Any]:
    """
    주제 정보를 바탕으로 답변하는 노드
    
    Args:
        state: 현재 그래프 상태
        
    Returns:
        업데이트된 상태
    """
    # 마지막 사용자 메시지 가져오기
    last: BaseMessage = state["messages"][-1]
    user_text = getattr(last, "content", "")
    
    # 주제 정보 로드
    subject_info = load_subject_info()
    
    # 메뉴 리스트를 문자열로 변환
    menu_str = "\n".join([f"- {menu}" for menu in subject_info["메뉴"]])
    
    # 프롬프트 생성 및 LLM 호출
    llm = get_chat_llm()
    msgs = SUBJECT_INFO_PROMPT.format_messages(
        name=subject_info["이름"],
        location=subject_info["위치"],
        type=subject_info["종류"],
        hours=subject_info["영업 시간"],
        phone=subject_info["전화번호"],
        menu=menu_str,
        user_message=user_text,
    )
    resp = llm.invoke(msgs)
    answer = getattr(resp, "content", str(resp))
    
    # AI 메시지 생성
    ai_message = AIMessage(content=answer)
    
    return {
        **state,
        "messages": state["messages"] + [ai_message],
        "current_node": "chat",         # 처리 후 chat로 복귀 (라우팅은 router가 판단)
        "subject_info": subject_info,
        "routing_decision": None,
    }

import json
import os
from typing import Dict, Any
from langchain_core.messages import AIMessage
from langchain_upstage import ChatUpstage
from langchain_core.prompts import ChatPromptTemplate
from st_app.utils.state import GraphState

# LLM 초기화
chat_model = ChatUpstage(model="solar-pro2")

def load_subject_info():
    """연돈 식당 정보를 로드합니다."""
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

# 주제 정보 프롬프트
SUBJECT_INFO_PROMPT = ChatPromptTemplate.from_template("""
당신은 연돈 식당에 대한 정보를 제공하는 전문 어시스턴트입니다.

다음은 연돈 식당의 기본 정보입니다:

**식당 정보:**
- 이름: {name}
- 위치: {location}
- 종류: {type}
- 영업시간: {hours}
- 전화번호: {phone}

**메뉴:**
{menu}

사용자의 질문에 대해 위 정보를 바탕으로 친근하고 도움이 되는 답변을 제공해주세요.
답변은 자연스럽고 대화체로 작성해주세요.

사용자 질문: {user_message}

답변:
""")

def subject_info_node(state: GraphState) -> Dict[str, Any]:
    """
    주제 정보를 바탕으로 답변하는 노드
    
    Args:
        state: 현재 그래프 상태
        
    Returns:
        업데이트된 상태
    """
    # 마지막 사용자 메시지 가져오기
    last_message = state["messages"][-1]
    user_message = last_message.content
    
    # 주제 정보 로드
    subject_info = load_subject_info()
    
    # 메뉴 리스트를 문자열로 변환
    menu_str = "\n".join([f"- {menu}" for menu in subject_info["메뉴"]])
    
    # 프롬프트 생성 및 LLM 호출
    prompt = SUBJECT_INFO_PROMPT.format(
        name=subject_info["이름"],
        location=subject_info["위치"],
        type=subject_info["종류"],
        hours=subject_info["영업 시간"],
        phone=subject_info["전화번호"],
        menu=menu_str,
        user_message=user_message
    )
    
    response = chat_model.invoke(prompt)
    
    # AI 메시지 생성
    ai_message = AIMessage(content=response.content)
    
    return {
        **state,
        "messages": state["messages"] + [ai_message],
        "current_node": "chat",  # 다시 채팅 노드로 복귀
        "subject_info": subject_info,
        "routing_decision": "return_to_chat"
    }

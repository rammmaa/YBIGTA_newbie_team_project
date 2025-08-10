from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

import streamlit as st
import os
import sys
from pathlib import Path

# st_app 디렉토리를 Python 경로에 추가
st_app_path = Path(__file__).parent / "st_app"
sys.path.append(str(st_app_path))

from langchain_core.messages import HumanMessage
from st_app.graph.router import create_router_graph, create_initial_state
import json

# # API 키 설정 (Streamlit Cloud secrets에서 가져오기)
if "UPSTAGE_API_KEY" in st.secrets:
    os.environ["UPSTAGE_API_KEY"] = st.secrets["UPSTAGE_API_KEY"]
elif "UPSTAGE_API_KEY" in os.environ:
    pass  # 이미 환경변수에 설정되어 있음
else:
    st.error("⚠️ UPSTAGE_API_KEY가 설정되지 않았습니다. Streamlit Cloud에서 API 키를 설정해주세요.")
    st.stop()

# 페이지 설정
st.set_page_config(
    page_title="연돈 챗봇",
    page_icon="🍽️",
    layout="wide"
)

# 세션 상태 초기화
if "messages" not in st.session_state:
    st.session_state.messages = []

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# LangGraph 초기화
if "router_graph" not in st.session_state:
    st.session_state.router_graph = create_router_graph()

# 사이드바 설정
with st.sidebar:
    st.title("🍽️ 연돈 챗봇")
    st.markdown("---")
    
    # 연돈 정보 표시
    st.subheader("📋 연돈 정보")
    try:
        with open("st_app/db/subject_information/subjects.json", "r", encoding="utf-8") as f:
            restaurant_info = json.load(f)
        
        st.write(f"**위치:** {restaurant_info['위치']}")
        st.write(f"**종류:** {restaurant_info['종류']}")
        st.write(f"**영업시간:** {restaurant_info['영업 시간']}")
        st.write(f"**전화번호:** {restaurant_info['전화번호']}")
        
        st.subheader("🍽️ 메뉴")
        for menu in restaurant_info['메뉴']:
            st.write(f"• {menu}")
            
    except Exception as e:
        st.error(f"정보를 불러올 수 없습니다: {e}")
    
    st.markdown("---")
    
    # 대화 초기화 버튼
    if st.button("🗑️ 대화 초기화"):
        st.session_state.messages = []
        st.session_state.chat_history = []
        st.rerun()

# 메인 채팅 인터페이스
st.title("🍽️ 연돈 챗봇")
st.markdown("연돈에 대한 질문을 해주세요! 메뉴, 위치, 영업시간 등 무엇이든 물어보세요.")

# 채팅 메시지 표시
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 사용자 입력
if prompt := st.chat_input("질문을 입력하세요..."):
    # 사용자 메시지 추가
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # 챗봇 응답 생성
    with st.chat_message("assistant"):
        with st.spinner("답변을 생성하고 있습니다..."):
            try:
                # LangGraph를 사용한 응답 생성
                # 현재 메시지를 LangChain 메시지 형식으로 변환
                langchain_messages = []
                for msg in st.session_state.messages:
                    if msg["role"] == "user":
                        langchain_messages.append(HumanMessage(content=msg["content"]))
                
                # 새로운 사용자 메시지 추가
                langchain_messages.append(HumanMessage(content=prompt))
                
                # 초기 상태 생성
                initial_state = create_initial_state(langchain_messages)
                
                # LangGraph 실행
                result = st.session_state.router_graph.invoke(initial_state)
                
                # 마지막 AI 메시지 가져오기
                last_ai_message = None
                for msg in result["messages"]:
                    if hasattr(msg, 'content') and msg != langchain_messages[-1]:
                        last_ai_message = msg
                
                if last_ai_message:
                    response_content = last_ai_message.content
                else:
                    response_content = "죄송합니다. 응답을 생성할 수 없습니다."
                
                # 응답 표시
                st.markdown(response_content)
                
                # 어시스턴트 메시지 추가
                st.session_state.messages.append({"role": "assistant", "content": response_content})
                
            except Exception as e:
                error_message = f"죄송합니다. 오류가 발생했습니다: {str(e)}"
                st.error(error_message)
                st.session_state.messages.append({"role": "assistant", "content": error_message})

# 하단 정보
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666;'>
    <p>💡 팁: "메뉴 추천해줘", "위치가 어디야?", "영업시간 알려줘" 등 질문해보세요!</p>
</div>
""", unsafe_allow_html=True)

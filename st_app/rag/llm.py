# st_app/rag/llm.py
import os
from typing import Callable

from langchain_upstage import ChatUpstage
from langchain_core.runnables import RunnablePassthrough, RunnableLambda
from langchain_core.output_parsers import StrOutputParser

from .prompt import RAG_PROMPT, CHAT_PROMPT, SUBJECT_INFO_PROMPT

from dotenv import load_dotenv
# .env 파일 로드
load_dotenv()

# 환경변수 (Streamlit Cloud에선 Secrets 권장)
UPSTAGE_API_KEY = os.getenv("UPSTAGE_API_KEY")
UPSTAGE_CHAT_MODEL = os.getenv("UPSTAGE_CHAT_MODEL", "solar-pro2")

if not UPSTAGE_API_KEY:
    raise ValueError("UPSTAGE_API_KEY가 설정되어 있지 않습니다. Secrets 또는 환경변수에 키를 넣어주세요.")

# 공용 LLM 인스턴스 (원하면 get_chat_llm으로 새로 만들 수도 있음)
chat = ChatUpstage(
    model=UPSTAGE_CHAT_MODEL,
    api_key=UPSTAGE_API_KEY,
    temperature=0.3,
    max_tokens=768,
)

def get_chat_llm(temperature: float = 0.3, max_tokens: int = 768) -> ChatUpstage:
    """일반 채팅/주제 노드에서 바로 쓰는 Upstage LLM 핸들러."""
    return ChatUpstage(
        model=UPSTAGE_CHAT_MODEL,
        api_key=UPSTAGE_API_KEY,
        temperature=temperature,
        max_tokens=max_tokens,
    )

def make_retriever_adapter(retriever_obj) -> RunnableLambda:
    """(question: str) -> context(str) 로 변환하는 어댑터."""
    def _to_context(question: str) -> str:
        hits = retriever_obj.retrieve(question)
        return retriever_obj.format_context(hits)
    return RunnableLambda(_to_context)

def get_rag_chain(retriever_obj) -> Callable[[str], str]:
    """
    retriever + 프롬프트 + Upstage LLM을 묶은 RAG 실행 함수(question -> answer).
    """
    retriever_adapter = make_retriever_adapter(retriever_obj)

    chain = (
        {
            "retrieved_reviews": retriever_adapter,       # question -> context(str)
            "user_message": RunnablePassthrough(),  # question 그대로
        }
        | RAG_PROMPT
        | chat
        | StrOutputParser()
    )

    def _run(question: str) -> str:
        return chain.invoke(question)

    return _run

import os
from langchain_upstage import ChatUpstage
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from .prompt import RAG_PROMPT

UPSTAGE_API_KEY = os.getenv("UPSTAGE_API_KEY")

API_URL = "https://api.upstage.ai/v1"

chat = ChatUpstage(model="solar-pro2")

def get_rag_chain(retriever):
    """
    RAG(Retrieval-Augmented Generation) 체인을 생성합니다.
    이 체인은 retriever를 통해 문서를 검색하고, LLM을 통해 최종 답변을 생성합니다.
    """
    rag_chain = (
        # retriever는 질문에 맞는 문맥(context)을 찾아냅니다.
        {"context": retriever, "question": RunnablePassthrough()}
        # RAG_PROMPT를 사용하여 문맥과 질문을 결합한 프롬프트를 만듭니다.
        | RAG_PROMPT
        # 프롬프트를 LLM에 전달하여 답변을 생성합니다.
        | chat
        # LLM의 출력을 문자열로 파싱합니다.
        | StrOutputParser()
    )
    return rag_chain

# def generate_response(prompt, max_tokens=512, temperature=0.7):
#     headers = {
#         "Authorization": f"Bearer {UPSTAGE_API_KEY}",
#         "Content-Type": "application/json",
#     }
#     data = {
#         "model": "solar-pro2", 
#         "prompt": prompt,
#         "max_tokens": max_tokens,
#         "temperature": temperature
#     }

#     response = requests.post(API_URL, headers=headers, json=data)
#     if response.status_code == 200:
#         result = response.json()
#         return result.get("text") or result.get("response") or "응답이 없습니다."
#     else:
#         raise Exception(f"Upstage API 에러: {response.status_code} - {response.text}")
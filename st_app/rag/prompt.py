from langchain_core.prompts import ChatPromptTemplate

SYSTEM_INSTRUCTION = """
# Overview
You are a helpful chatbot that provides information about 연돈 restaurant.
You should always provide accurate and helpful responses based on the context information provided.
"""

RAG_PROMPT = ChatPromptTemplate.from_template("""
{system_instruction}

[Context]
{context}

[Question]
{question}

Please answer the question based on the above context. If the context doesn't contain enough information to answer the question, please say so politely.
""")

# 채팅 프롬프트 
CHAT_PROMPT = ChatPromptTemplate.from_template("""
당신은 친근하고 도움이 되는 AI 어시스턴트입니다. 
사용자와 자연스럽게 대화하며, 연돈 식당에 대한 질문이 있으면 적절히 답변해주세요.

사용자 메시지: {user_message}

답변:
""")

# 식당 정보 프롬프트
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

def make_prompt(question, retrieved_texts):
    context = "\n".join(f"- {text}" for text in retrieved_texts)
    return f"""{SYSTEM_INSTRUCTION}

[Context]
{context}

[Question]
{question}

Please answer the question based on the above context.
"""

# st_app/rag/prompt.py
from langchain.prompts import ChatPromptTemplate

# 리뷰 기반 RAG 프롬프트
RAG_PROMPT = ChatPromptTemplate.from_template("""
당신은 연돈 식당에 대한 리뷰 정보를 제공하는 전문 어시스턴트입니다.

다음은 연돈에 대한 실제 고객 리뷰들입니다:

**검색된 리뷰 내용:**
{retrieved_reviews}

사용자의 질문에 대해 위 리뷰 정보를 바탕으로 친근하고 도움이 되는 답변을 제공해주세요.
리뷰 내용을 인용하거나 요약하여 답변해주세요.
답변은 자연스럽고 대화체로 작성해주세요.

만약 검색된 리뷰가 충분하지 않다면, 그 점을 언급하고 가능한 범위 내에서 답변해주세요.

사용자 질문: {user_message}

답변:
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

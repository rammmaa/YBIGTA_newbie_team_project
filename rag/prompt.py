from langchain_upstage import PromptTemplate

SYSTEM_INSTRUCTION = """
# Overview
You are a chatbot that delivers the latest news to users.
You should always use tools to retrieve the latest news and provide appropriate responses based on this information.
"""

RAG_PROMPT = PromptTemplate(
    template=prompt_template,
    input_variables=["context", "question:"]
)

def make_prompt(question, retrieved_texts):
    context = "\n".join(f"- {text}" for text in retrieved_texts)
    return f"""{SYSTEM_INSTRUCTION}

[Context]
{context}

[Question]
{question}

Please answer the question based on the above context.
"""

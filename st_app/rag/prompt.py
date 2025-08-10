from langchain_core.prompts import PromptTemplate

SYSTEM_INSTRUCTION = """
# Overview
You are a helpful chatbot that provides information about 연돈 restaurant.
You should always provide accurate and helpful responses based on the context information provided.
"""

prompt_template = """
{system_instruction}

[Context]
{context}

[Question]
{question}

Please answer the question based on the above context. If the context doesn't contain enough information to answer the question, please say so politely.
"""

RAG_PROMPT = PromptTemplate(
    template=prompt_template,
    input_variables=["system_instruction", "context", "question"]
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

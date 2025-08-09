from retriever import Retriever
from prompt import make_prompt
from llm import generate_response

def main():
    index_path = "../db/faiss_index/index.faiss"
    meta_path = "../db/faiss_index/meta.json"

    retriever = Retriever(index_path, meta_path)

    while True:
        question = input("질문을 입력하세요 (종료: exit): ")
        if question.lower() == "exit":
            break

        indices, distances = retriever.search(question, top_k=5)
        # indices를 바탕으로 리뷰 텍스트를 가져오는 로직 필요
        # 예) 리뷰 텍스트를 따로 저장하거나 retriever에 저장해두고 참조

        # 임시 예시 (텍스트 리스트는 별도 구현 필요)
        retrieved_texts = ["리뷰1 텍스트", "리뷰2 텍스트", "리뷰3 텍스트"]

        prompt = make_prompt(question, retrieved_texts)
        answer = generate_response(prompt)
        print("\n[답변]")
        print(answer)
        print("-" * 30)

if __name__ == "__main__":
    main()
import faiss
import json
import numpy as np
from sentence_transformers import SentenceTransformer
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # st_app 폴더 - 경로 2번 올라감. - 여기에 db 폴더가 있다
PROJECT_ROOT = os.path.dirname(BASE_DIR)  # project_root 경로 # BASE_DIR에서 1번 올라감. - 여기에 database 폴더가 있다

index_dir = os.path.join(BASE_DIR, "db", "faiss_index")
index_file = "index.faiss"
index_path = os.path.join(index_dir, index_file)

def get_retriever():
    """
    FAISS 벡터 데이터베이스에서 retriever 객체를 로드하고 반환합니다.
    이 객체는 사용자의 질문과 가장 유사한 문서를 검색하는 역할을 합니다.
    """
    # 인덱스 파일이 존재하는지 확인합니다.
    if not os.path.exists(index_path):
        raise FileNotFoundError(
            f"FAISS 인덱스 파일이 없습니다: {index_path}\n"
            f"먼저 문서를 임베딩하여 인덱스 파일을 생성해야 합니다."
        )

    # Upstage 임베딩 모델을 초기화합니다.
    embeddings = UpstageEmbeddings()

    # 저장된 FAISS 인덱스를 로드합니다.
    db = FAISS.load_local(
        folder_path=index_dir,
        embeddings=embeddings,
        index_name="index",
        # 인덱스 파일을 명시적으로 로드합니다.
        allow_dangerous_deserialization=True  
    )

    # FAISS 데이터베이스에서 retriever 객체를 생성합니다.
    # search_kwargs={"k": 3}는 질문과 가장 유사한 문서 3개를 검색하도록 설정합니다.
    retriever = db.as_retriever(search_kwargs={"k": 3})
    
    return retriever

# 1. 경로 설정
# reviews_dir = os.path.join(PROJECT_ROOT, "database")  # CSV 파일 있는 폴더
# save_dir = os.path.join(BASE_DIR, "db", "faiss_index")  # index.faiss 저장 폴더
# index_path = os.path.join(save_dir, "index.faiss")
# meta_path = os.path.join(save_dir, "meta.json")

# class Retriever:
#     def __init__(self, index_path, meta_path, docs):
#         self.index = faiss.read_index(index_path)
#         with open(meta_path, 'r', encoding='utf-8') as f:
#             self.meta = json.load(f)
#         self.model = SentenceTransformer(self.meta['embedding_model'])
#         self.docs = docs  # 원본 문서 리스트 (인덱스 번호와 매칭)

#     def search(self, query, top_k=5):
#         q_emb = self.model.encode([query], convert_to_numpy=True).astype(np.float32)
#         distances, indices = self.index.search(q_emb, top_k)
#         results = []
#         for idx in indices[0]:
#             results.append(self.docs[idx])
#         return results, distances[0]
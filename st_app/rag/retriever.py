import os
import json
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

# 경로 설정
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INDEX_DIR = os.path.join(BASE_DIR, "db", "faiss_index")
INDEX_PATH = os.path.join(INDEX_DIR, "index.faiss")
META_PATH = os.path.join(INDEX_DIR, "meta.json")

class ReviewRetriever:
    def __init__(self, top_k: int = 3):
        # 인덱스와 메타 파일 확인
        if not os.path.exists(INDEX_PATH):
            raise FileNotFoundError(f"FAISS 인덱스 없음: {INDEX_PATH}")
        if not os.path.exists(META_PATH):
            raise FileNotFoundError(f"meta.json 없음: {META_PATH}")

        # meta.json 로드
        with open(META_PATH, "r", encoding="utf-8") as f:
            meta = json.load(f)

        self.embed_model_name = meta.get("embedding_model", "all-MiniLM-L6-v2")
        self.metric = meta.get("metric", "L2")
        self.top_k = top_k

        # FAISS 인덱스 로드
        self.index = faiss.read_index(INDEX_PATH)

        # docs.jsonl 로드
        docs_path = meta.get("docs_path", os.path.join(INDEX_DIR, "docs.jsonl"))
        if not os.path.exists(docs_path):
            raise FileNotFoundError(f"docs.jsonl 없음: {docs_path}")

        with open(docs_path, "r", encoding="utf-8") as f:
            self.docs = [json.loads(line) for line in f]

        # 인덱스-문서 개수 검증
        if self.index.ntotal != len(self.docs):
            raise ValueError(f"인덱스({self.index.ntotal})와 문서({len(self.docs)}) 개수가 불일치")

        # SentenceTransformer 임베딩 모델 로드
        self.model = SentenceTransformer(self.embed_model_name)

    def retrieve(self, query: str) -> list[dict]:
        # 쿼리 임베딩
        q_vec = self.model.encode([query], convert_to_numpy=True).astype(np.float32)

        # 검색
        D, I = self.index.search(q_vec, self.top_k)

        # 결과 구성
        hits = []
        for idx, dist in zip(I[0], D[0]):
            if idx == -1:
                continue
            doc = self.docs[idx]
            hits.append({
                "text": doc.get("content", ""),
                "subject_id": doc.get("subject_id"),
                "score": float(dist),
                "meta": {k: v for k, v in doc.items() if k != "content"}
            })
        return hits

    def format_context(self, hits: list[dict]) -> str:
        """검색 결과를 RAG 프롬프트 컨텍스트로 변환"""
        if not hits:
            return "컨텍스트 없음"
        lines = []
        for h in hits:
            tag = h.get("subject_id") or h["meta"].get("site_name") or "doc"
            lines.append(f"- ({tag}) {h['text']}")
        return "\n".join(lines)

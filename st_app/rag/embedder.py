import os
import glob
import json
from datetime import datetime
import pandas as pd
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer

# 현재 스크립트 경로 기준으로 상위 구조 계산
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # st_app/
PROJECT_ROOT = os.path.dirname(BASE_DIR)  # repo root

# 1. 경로 설정
reviews_dir = os.path.join(PROJECT_ROOT, "database")               # CSV 폴더
save_dir    = os.path.join(BASE_DIR, "db", "faiss_index")          # index 저장 폴더
index_path  = os.path.join(save_dir, "index.faiss")
meta_path   = os.path.join(save_dir, "meta.json")
docs_path   = os.path.join(save_dir, "docs.jsonl")                 #  추가: 문서 매핑

os.makedirs(save_dir, exist_ok=True)

# 2. 전처리 리뷰 파일 읽기
file_list = glob.glob(os.path.join(reviews_dir, "preprocessed_reviews_*.csv"))
df_list = []

for file in file_list:
    try:
        df = pd.read_csv(file)
        df_list.append(df)
        print(f"✅ {file} 읽기 완료 (행 {len(df)})")
    except Exception as e:
        print(f"❌ {file} 읽기 실패: {e}")

if not df_list:
    raise ValueError("preprocessed_reviews 파일을 찾을 수 없습니다.")

all_reviews = pd.concat(df_list, ignore_index=True)

# 3. 텍스트 컬럼 지정 + 전처리(★ 중요)
if "content" not in all_reviews.columns:
    raise ValueError("'content' 컬럼이 없습니다. 실제 컬럼명 확인 필요.")

# 결측/공백 제거
all_reviews = all_reviews.dropna(subset=["content"])
all_reviews["content"] = all_reviews["content"].astype(str).str.strip()

# 너무 짧은 텍스트 제거(길이<5)
all_reviews = all_reviews[all_reviews["content"].str.len() >= 5]

# 완전 중복 제거
all_reviews = all_reviews.drop_duplicates(subset=["content"]).reset_index(drop=True)

# 필요하다면 날짜/사이트 기준 정렬(재현성 ↑) — 컬럼 없으면 무시
sort_cols = [c for c in ["date", "site_name", "rating"] if c in all_reviews.columns]
if sort_cols:
    all_reviews = all_reviews.sort_values(sort_cols).reset_index(drop=True)

texts = all_reviews["content"].tolist()
print(f"🧹 전처리 후 문서 수: {len(texts)}")

# 4. 임베딩 모델 로드
embedding_model_name = "all-MiniLM-L6-v2"
model = SentenceTransformer(embedding_model_name)

# 5. 문장 → 벡터 변환 (배치 인코딩 권장)
embeddings = model.encode(
    texts,
    batch_size=128,               # 필요시 조정
    show_progress_bar=True,
    convert_to_numpy=True,
    normalize_embeddings=False    # L2 인덱스이므로 정규화 X
).astype(np.float32)

# 6. FAISS 인덱스 생성 (L2 거리)  ★ retriever도 L2로 맞출 것
d = embeddings.shape[1]
index = faiss.IndexFlatL2(d)

# 7. 인덱스에 벡터 추가
index.add(embeddings)
print(f"📦 인덱스에 추가된 벡터 수: {index.ntotal}")

# 8. 인덱스 저장
faiss.write_index(index, index_path)
print(f"💾 인덱스 저장 완료: {index_path}")

# 9. 문서 매핑 저장(★ 중요: 인덱스 순서 == 파일 기록 순서)
with open(docs_path, "w", encoding="utf-8") as f:
    for i, row in all_reviews.iterrows():
        rec = {
            "id": row.get("id", f"doc_{i}"),
            "content": row["content"],
            "site_name": row.get("site_name"),
            "rating": row.get("rating"),
            "date": row.get("date"),
            "subject_id": row.get("subject_id"),
            "source": row.get("source"),   # 있으면 기록
        }
        f.write(json.dumps(rec, ensure_ascii=False) + "\n")
print(f"🗃️ docs.jsonl 저장 완료: {docs_path}")

# 10. 메타 저장(임베딩-검색 일관성 기록)
meta_data = {
    "embedding_model": embedding_model_name,
    "vector_dimension": d,
    "index_type": "IndexFlatL2",
    "metric": "L2",                     # retriever 참고용
    "total_vectors": int(index.ntotal),
    "created_at": datetime.now().isoformat(),
    "source_files": [os.path.basename(f) for f in file_list],
    "docs_path": docs_path              # ★ retriever가 이 경로를 로드
}

with open(meta_path, "w", encoding="utf-8") as f:
    json.dump(meta_data, f, ensure_ascii=False, indent=4)

print(f"📝 메타데이터 저장 완료: {meta_path}")

import os
import glob
import json
from datetime import datetime
import pandas as pd
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer

# 현재 스크립트 경로 기준으로 상위 구조 계산
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # st_app 폴더 - 경로 2번 올라감.
PROJECT_ROOT = os.path.dirname(BASE_DIR)  # project_root 경로 # BASE_DIR에서 1번 올라감.

# 1. 경로 설정
reviews_dir = os.path.join(PROJECT_ROOT, "database")  # CSV 파일 있는 폴더
save_dir = os.path.join(BASE_DIR, "db", "faiss_index")  # index.faiss 저장 폴더
index_path = os.path.join(save_dir, "index.faiss")
meta_path = os.path.join(save_dir, "meta.json")

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

# 하나의 DataFrame으로 합치기
if not df_list:
    raise ValueError("preprocessed_reviews 파일을 찾을 수 없습니다.")
all_reviews = pd.concat(df_list, ignore_index=True)

# 3. 텍스트 컬럼 지정
# 'review' 컬럼명은 실제 데이터에 맞게 변경
if "content" not in all_reviews.columns:
    raise ValueError("'content' 컬럼이 없습니다. 실제 컬럼명 확인 필요.")
texts = all_reviews["content"].astype(str).tolist()

# 4. 임베딩 모델 로드
embedding_model_name = "all-MiniLM-L6-v2"
model = SentenceTransformer(embedding_model_name)

# 5. 문장 → 벡터 변환
embeddings = model.encode(texts, show_progress_bar=True)
embeddings = np.array(embeddings, dtype=np.float32)

# 6. FAISS 인덱스 생성 (L2 거리)
d = embeddings.shape[1]
index = faiss.IndexFlatL2(d)

# 7. 인덱스에 벡터 추가
index.add(embeddings)
print(f"📦 인덱스에 추가된 벡터 수: {index.ntotal}")

# 8. 저장 경로 생성
os.makedirs(os.path.dirname(index_path), exist_ok=True)

# 9. 인덱스 저장
faiss.write_index(index, index_path)
print(f"💾 인덱스 저장 완료: {index_path}")

meta_data = {
    "embedding_model": embedding_model_name,
    "vector_dimension": d,
    "index_type": "IndexFlatL2",
    "total_vectors": int(index.ntotal),
    "created_at": datetime.now().isoformat(),
    "source_files": [os.path.basename(f) for f in file_list]
}

with open(meta_path, "w", encoding="utf-8") as f:
    json.dump(meta_data, f, ensure_ascii=False, indent=4)

print(f"📝 메타데이터 저장 완료: {meta_path}")
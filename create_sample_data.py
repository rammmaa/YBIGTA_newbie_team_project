import os
import json
import pandas as pd
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer
from datetime import datetime

def create_sample_reviews():
    """샘플 리뷰 데이터를 생성합니다."""
    sample_reviews = [
        "연돈의 돈까스가 정말 맛있어요! 바삭하고 촉촉해서 최고입니다.",
        "위치가 조금 찾기 어렵지만 맛은 정말 좋아요. 특히 치즈까스 추천합니다.",
        "영업시간이 12시부터 21시까지라 점심시간에 가기 좋아요.",
        "제주도 여행 중에 들렀는데 정말 만족스러웠습니다. 하이라이스도 맛있어요.",
        "가격대비 양이 많고 맛있어서 가성비가 좋은 식당입니다.",
        "카레도 맛있고 돈까스도 맛있어서 다음에 또 가고 싶어요.",
        "직원분들이 친절하고 서비스도 좋았습니다.",
        "볼카츠 박스로 포장해서 가져가기 좋아요.",
        "연돈 도시락도 맛있어서 점심 메뉴로 추천합니다.",
        "제주 서귀포에 있는 돈까스 맛집이라고 소문난 곳이에요."
    ]
    
    # CSV 파일로 저장
    df = pd.DataFrame({
        'content': sample_reviews,
        'rating': [5, 4, 5, 5, 4, 5, 4, 4, 5, 5],
        'date': pd.date_range('2024-01-01', periods=len(sample_reviews))
    })
    
    # database 디렉토리 생성
    os.makedirs('database', exist_ok=True)
    df.to_csv('database/preprocessed_reviews_sample.csv', index=False, encoding='utf-8')
    print("✅ 샘플 리뷰 데이터 생성 완료")

def create_faiss_index():
    """FAISS 인덱스를 생성합니다."""
    # 샘플 리뷰 데이터 로드
    df = pd.read_csv('database/preprocessed_reviews_sample.csv')
    texts = df['content'].tolist()
    
    # 임베딩 모델 로드
    model = SentenceTransformer('all-MiniLM-L6-v2')
    
    # 임베딩 생성
    embeddings = model.encode(texts, show_progress_bar=True)
    embeddings = np.array(embeddings, dtype=np.float32)
    
    # FAISS 인덱스 생성
    d = embeddings.shape[1]
    index = faiss.IndexFlatL2(d)
    index.add(embeddings)
    
    # 저장 경로 생성
    save_dir = 'st_app/db/faiss_index'
    os.makedirs(save_dir, exist_ok=True)
    
    # 인덱스 저장
    index_path = os.path.join(save_dir, 'index.faiss')
    faiss.write_index(index, index_path)
    
    # 메타데이터 저장
    meta_data = {
        "embedding_model": "all-MiniLM-L6-v2",
        "vector_dimension": d,
        "index_type": "IndexFlatL2",
        "total_vectors": int(index.ntotal),
        "created_at": datetime.now().isoformat(),
        "source_files": ["preprocessed_reviews_sample.csv"]
    }
    
    meta_path = os.path.join(save_dir, 'meta.json')
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(meta_data, f, ensure_ascii=False, indent=4)
    
    print("✅ FAISS 인덱스 생성 완료")

def main():
    """메인 실행 함수"""
    print("🚀 샘플 데이터 생성 시작...")
    
    # 샘플 리뷰 데이터 생성
    create_sample_reviews()
    
    # FAISS 인덱스 생성
    create_faiss_index()
    
    print("🎉 모든 샘플 데이터 생성 완료!")

if __name__ == "__main__":
    main()

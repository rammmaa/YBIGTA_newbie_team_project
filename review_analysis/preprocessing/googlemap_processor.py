import os
import re
import pandas as pd # type: ignore
import numpy as np # type: ignore
from gensim.models import Word2Vec # type: ignore
from nltk.tokenize import word_tokenize # type: ignore
from nltk.corpus import stopwords # type: ignore
import nltk # type: ignore
from review_analysis.preprocessing.base_processor import BaseDataProcessor

nltk.download('punkt')
nltk.download('stopwords')
nltk.download('punkt_tab')

class GooglemapProcessor(BaseDataProcessor):
    """
    Googlemap 리뷰 데이터를 전처리 및 특징 추출하는 클래스
    """
    def __init__(self, input_path: str, output_path: str):
        """
        GooglemapProcessor 생성자.
        Args:
            input_path (str): 입력 CSV 파일 경로
            output_path (str): 출력 디렉토리 경로
        """
        super().__init__(input_path, output_path)
        self.df = None
        self.embeddings = None

    def preprocess(self):
        """
        CSV 파일을 불러와서 전처리합니다."""
        # CSV 파일 불러오기
        df = pd.read_csv(self.input_path)

        # text 컬럼을 content로 변경
        df = df.rename(columns={"text": "content"})

        # rating, content, date 결측치 제거
        df = df.dropna(subset=["rating", "content", "date"])

        # rating이 숫자가 아닌 경우 제거, 1~5 범위 밖 제거
        df["rating"] = pd.to_numeric(df["rating"], errors="coerce")
        df = df[df["rating"].between(1, 5)]

        # 날짜 형식 변환
        df["date"] = pd.to_datetime(df["date"], errors="coerce")
        df = df.dropna(subset=["date"])

        # 리뷰 길이가 너무 짧거나 긴 경우 제거
        df["content"] = df["content"].astype(str)
        df["review_len"] = df["content"].str.len()
        df = df[(df["review_len"] >= 3) & (df["review_len"] <= 1800)]

        # 과거/미래 날짜 제거
        today = pd.Timestamp.today()
        df = df[(df["date"] >= "2015-01-01") & (df["date"] <= today)]

        # 텍스트 정제
        df["clean_text"] = df["content"].apply(self._clean_text)

        self.df = df.reset_index(drop=True)

        
    def feature_engineering(self):
        """
        텍스트 토큰화, Word2Vec 벡터화, 요일 파생변수 생성
        """
        # 토큰화 및 불용어 제거
        self.df["tokens"] = self.df["clean_text"].apply(word_tokenize)
        stop_words = set(stopwords.words('english'))
        self.df["tokens"] = self.df["tokens"].apply(lambda x: [w for w in x if w.lower() not in stop_words])

        # Word2Vec 학습
        model = Word2Vec(sentences=self.df["tokens"], vector_size=50, window=5, min_count=1, workers=4)
        self.embeddings = model

        # 각 리뷰를 평균 벡터로 변환하고 문자열로 저장
        def vector_to_string(tokens):
            vectors = [model.wv[word] for word in tokens if word in model.wv]
            avg_vec = np.mean(vectors, axis=0) if vectors else np.zeros(50)
            return "[" + ", ".join(f"{v:.4f}" for v in avg_vec) + "]"

        self.df["vector"] = self.df["tokens"].apply(vector_to_string)

        # 요일 파생변수 (0=월요일, 6=일요일)
        self.df["weekday"] = self.df["date"].dt.weekday

    def save_to_database(self):
        """
        self.df를 CSV 파일로 저장.
        """
        result = self.df[["rating", "content", "date", "weekday", "vector"]]
        save_path = os.path.join(self.output_dir, "preprocessed_reviews_googlemap.csv")
        result.to_csv(save_path, index=False)
        print(f"저장 완료: {save_path}")



    def _clean_text(self, text: str) -> str:
        """
        텍스트 정제 함수 - 특수문자 제거 및 소문자 변환
        """
        text = re.sub(r"[^\w\s]", " ", text)  # 특수문자 제거
        text = re.sub(r"\s+", " ", text).strip()  # 공백 정리
        return text.lower()


### 팀 소개

짱짱팀입니당~^^
(할말있으시면 쓰셔도 됨)

## 이하람

- 컴퓨터과학과 24학번  
- MBTI: ISTJ  
- 좋아하는 것: 피아노, 밴드, 뜨개질, 문학, 차, 만년필, 뜨개질, 이외 다수… 취미부자…  
- 기타: 국제캠퍼스 무악하우스 RA(25-1, 2), 모르고리즘 운영진, 신촌ICPC 2025-s 운영진, RCM/관설차회 등 소속  
- 특이사항: 아직 뭘 할지 잘 모르겠다…!!

## 김현수

## 조재관

- 컴퓨터과학과 21학번  
- MBTI: ENTP(INTP)  
- 좋아하는 것: 운동(축구, 약구, 헬스, 러닝 등등), 여행

---

### 코드 실행 방법

## Web

1. 가상환경(venv) 만들기 및 활성화 

```
python -m venv venv
# Windows
venv\Scripts\activate
# Mac/Linux
source venv/bin/activate
````

2. 필요 패키지 설치

```
pip install -r requirements.txt
```

3. FastAPI 앱 실행

```
uvicorn app.main:app --reload
```

4. 웹 브라우저 접속

* `http://localhost:8000` 
* `http://localhost:8000/static/index.html` 

5. API 테스트 (예: 로그인 등)

* `http://localhost:8000/api/user/login` 같은 API 엔드포인트에 POST 요청 보내서 테스트 가능

---

## 크롤링

1. 프로젝트 루트 디렉토리에서 아래 명령어 실행

* 전체 사이트 크롤링 실행

```
python review_analysis/crawling/main.py -o database --all
```

* 특정 사이트만 실행

```
python review_analysis/crawling/main.py -o database --site {사이트이름}
```

2. 크롤링 결과 저장 위치

```
database/reviews_{사이트이름}.csv
```

예: `reviews_kakao.csv`, `reviews_naver.csv` 등

---

## EDA/FE

1. 가상환경(venv) 만들기 및 활성화 

```
python -m venv venv
# Windows
venv\Scripts\activate
# Mac/Linux
source venv/bin/activate
````

2. 필요 패키지 설치

```
pip install -r requirements.txt
```
3. 
```
python review_analysis/preprocessing/main.py --output_dir database --all
```

4. 프로그램 실행 시 아래 디렉토리에 파일 저장

database/
├── preprocessed_reviews_{사이트이름1}.csv
├── preprocessed_reviews_{사이트이름2}.csv
...

5. 시각화: review_analysis/plots 디렉토리에 이미지 저장되어 있음


YBIGTA_newbie_team_project/review_analysis/eda/visualization에서 .py 확인 가능

 preprocessed_reviews_{사이트이름}.csv과 같은 경로에서 다음 파일 실행 시 시각화 확인 가능
 
 1. monthly_review_count_by_platform.py

2. rating_distribution_by_platform.py

3. lineplot_monthly_rating_by_platform.py

4. tsne_sentiment_text_distribution.py

5. weekly_review_count_by_platform.py
 

![이미지1](https://i.imgur.com/niDtCoG.jpg)
![이미지2](https://i.imgur.com/FB4KpiX.jpg)
![이미지3](https://imgur.com/LsOR612.jpg)




### 팀 소개

짱짱팀입니당~^^

## 이하람

- 컴퓨터과학과 24학번  
- MBTI: ISTJ  
- 좋아하는 것: 피아노, 밴드, 뜨개질, 문학, 차, 만년필, 뜨개질, 이외 다수… 취미부자…  
- 기타: 국제캠퍼스 무악하우스 RA(25-1, 2), 모르고리즘 운영진, 신촌ICPC 2025-s 운영진, RCM/관설차회 등 소속  
- 특이사항: 아직 뭘 할지 잘 모르겠다…!!

## 김현수

- 응용통계학과 23학번
- MBTI: INTJ (1년 전까진 INFJ)
- 특기: 일 벌리기, 취미: 일 미루기

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
venv\Scripts\activate # Windows
source venv/bin/activate # Mac/Linux
````

2. 디렉토리로 이동 > 필요 패키지 설치

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

```
YBIGTA_newbie_team_project
├── README.md # 읽어주세요...
│
├── database/
│ ├── reviews_{사이트 이름}.csv
│ └──
...
│
├── review_analysis/
│ ├── crawling/
│ │ ├── base_crawler.py
│ │ ├── main.py
│ │ └──
...
│ └──
...
└──... // 
```

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

---

## EDA/FE & 시각화

1. 가상환경(venv) 만들기 및 활성화 

```
python -m venv venv 
venv\Scripts\activate # Windows
source venv/bin/activate # Mac/Linux
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

5. 비교분석

    vector 열에 저장된 word2vec 결과 vector_list 열에 리스트 형태로 저장
    
    각 사이트별 'rating'열에 대한 describe진행.
    평균, min, max 확인
    
    dt.year, dt.to_period("M") 이용하여 date 데이터에서 연도, 연도+월 추출
    
    1. 각 사이트별 특정 키워드 언급 수 비교
        '동네' 키워드 언급 수 비교
        '백종원' 키워드 언급 수 비교
    
    2. 요일에 따른 평균 별점 비교
        특정 요일에 평균이 낮은 것 확인
    
    3. 시간(월 단위)에 따른 평균 별점 추이
        시각화하였을 때, 계절성이 있는 것처럼 보이기도 함.
        계속해서 일정한 폭의 변동이 있지만, 점점 낮아지는 추세를 보임. 
<Figure size 640x480 with 1 Axes><img width="556" height="449" alt="image" src="https://github.com/user-attachments/assets/7a30060f-ba36-4de0-955c-ae957b37bc59" />
        캐치테이블

<Figure size 640x480 with 1 Axes><img width="556" height="449" alt="image" src="https://github.com/user-attachments/assets/e737980f-1c66-46cd-9608-cd513ea3a96f" />
        카카오맵


    4. 사이트별 긍정 리뷰, 부정 리뷰 비율 비교
        별점 2점 이하는 부정, 4-5점은 긍정으로 처리.
        kakao map과 google map을 비교하였을 때, 
        google map에서 긍정 리뷰 비율이 더 높은 것으로 나타남.
    

5. 시각화: review_analysis/plots 디렉토리에 이미지 저장되어 있음
=======
1) 결측치 및 이상치 처리
rating, content, date 컬럼에 결측치가 있는 행 제거

rating은 숫자로 변환 후 1~5 사이 값만 유지

date는 파싱 실패한 값 제거 및 2015년 이전·미래 날짜 제외

content 길이가 3자 미만 또는 1800자 초과인 경우 제거

2) 텍스트 전처리 및 파생변수 생성
content에서 특수문자 제거, 공백 정리, 소문자 변환하여 clean_text 생성

clean_text에 대해 word_tokenize 수행 후 불용어 제거하여 tokens 생성

date를 기반으로 요일 정보(weekday: 0~6) 추출하여 파생변수 생성

3) 텍스트 벡터화
tokens 컬럼을 활용해 Word2Vec 임베딩 모델 학습 (vector_size=50)

각 리뷰의 단어 벡터 평균을 계산해 고정 길이 벡터(vector) 생성

최종적으로 rating, content, date, weekday, vector 컬럼으로 구성된 CSV 저장

5. 시각화: review_analysis/plots 디렉토리에 이미지 저장되어 있음

1)  월별 리뷰 개수 (플랫폼별)
Googlemap은 초반에 리뷰가 많았으나, 시간이 지날수록 점차 감소세를 보임.

Kakaomap은 2023년부터 꾸준히 리뷰가 달리기 시작했으며, 안정적인 증가세를 보임.

Catchtable은 2024년 이후부터 급격히 리뷰 수가 늘어나는 모습을 보이며, 최근에는 가장 많은 리뷰를 기록함.

![이미지](review_analysis/plots/1.png)

2) 월별 평균 별점 추이 (플랫폼별)
Catchtable은 전반적으로 평균 별점이 매우 높고, 거의 5점에 가까운 수준을 꾸준히 유지함.

Googlemap은 시간이 흐를수록 평균 별점이 서서히 낮아지는 추세를 보임.

Kakaomap은 별점 편차가 크며, 특히 낮은 별점이 자주 나타나는 경향을 보임.

![이미지](review_analysis/plots/2.png)

3) 플랫폼별 별점 분포 (Boxplot)
Catchtable은 대부분 5점에 집중되어 있고, 별점 편차도 크지 않음.

Googlemap은 중간값이 4점이지만, 낮은 별점(1~2점)도 일부 존재해 분포가 넓은 편임.

Kakaomap은 전반적으로 별점 분산이 크며, 중간값은 4점이지만 2점 이하의 리뷰도 자주 나타남.

![이미지](review_analysis/plots/3.png)

4-1) Word2Vec 임베딩 + t-SNE 시각화 (별점 색깔)
전반적으로 별점이 높을수록 외곽으로 퍼지는 경향을 보임.

중심부에는 별점이 낮은 리뷰들이 몰려 있는 모습이 나타남.

고평점(노란색)은 다소 분산돼 있고, 저평점(보라색 계열)은 군집화되어 있음.
.

4-2) 클러스터 0번이 전체의 대부분을 차지하며 중심에 위치함.

클러스터 1, 3, 4 등은 외곽에 소수 분포하고 있음.

일부 클러스터는 특정 테마나 리뷰 내용이 유사한 집단일 가능성이 있음.


![이미지](review_analysis/plots/4-1.png)
![이미지](review_analysis/plots/4-2.png)

5)  요일별 리뷰 개수 (플랫폼별)
Googlemap은 월요일과 목요일에 리뷰가 몰리는 경향을 보임.

Kakaomap은 수요일과 토요일에 리뷰가 많고, 금요일에는 비교적 적은 편임.

Catchtable은 수요일, 금요일, 토요일에 리뷰가 집중됨.

![이미지](review_analysis/plots/5.png)


YBIGTA_newbie_team_project/review_analysis/eda/visualization에서 .py 확인 가능

 preprocessed_reviews_{사이트이름}.csv과 같은 경로에서 다음 파일 실행 시 시각화 확인 가능
 
 1. monthly_review_count_by_platform.py

2. rating_distribution_by_platform.py

3. lineplot_monthly_rating_by_platform.py

4. tsne_sentiment_text_distribution.py

5. weekly_review_count_by_platform.py
 
![이미지2](https://i.imgur.com/FB4KpiX.jpg)
![이미지1](https://i.imgur.com/niDtCoG.jpg)
![이미지3](https://imgur.com/LsOR612.jpg)

---
## DB, Docker, AWS

### github_action.png
<img width="1156" height="389" alt="action" src="https://github.com/user-attachments/assets/e179ed07-8e02-48b2-a17c-38dd28a25642" />

### docker hub 주소
docker.io/rammma/my-fastapi-app

### preprocess(사이트).png
![1](aws/preprocess.png)

<img width="625" height="431" alt="preprocess(googlemap)" src="https://github.com/user-attachments/assets/ebcd4d53-3541-44f4-9919-567bff3d069a" />
<img width="725" height="499" alt="preprocess(kakaomap)" src="https://github.com/user-attachments/assets/840b2d91-28ab-4524-908d-a8e464c0e052" />

### login.png
![1](aws/login.png)

### register.png
![1](aws/register.png)

### update_password.png
![1](aws/update-password.JPG)

### mongoDB.png
<img width="1078" height="279" alt="mongoDB" src="https://github.com/user-attachments/assets/1b9bef09-6495-424f-8b0e-a58a65d2b66a" />


## 1. RDS 보안 설정: 퍼블릭 액세스 차단 & VPC 내부 접속 허용

* AWS RDS 인스턴스는 보안을 위해 퍼블릭 액세스를 허용하지 않고, VPC 내에서만 접속 가능하도록 설정하였다.


1) RDS 생성 시 “퍼블릭 액세스” 옵션을 No로 설정
2) RDS가 속한 VPC 및 서브넷을 확인
3) 보안 그룹(Security Group)에서 EC2 인스턴스가 속한 서브넷 또는 IP만 인바운드 허용
    이를 통해 EC2와 RDS 간 안전한 사설 네트워크 통신이 가능하도록 구성

![1](aws/ad1.png)
![1](aws/ad2.png)


## 2. 로드 밸런서를 통한 포트 외부 노출 최소화

EC2 인스턴스는 외부에 직접 포트를 노출하지 않고, AWS Elastic Load Balancer (ELB)를 활용해 트래픽을 분산하였다.

로드 밸런서는 외부 요청을 받아 내부 EC2 인스턴스로 전달하며,
EC2는 로드 밸런서가 사용하는 포트(예: 80, 443) 외에는 외부 접근을 차단하도록 설정했다.

![1](aws/av1.png)
![1](aws/av2.png)


## 3. 프로젝트를 진행하며 깨달은 점, 마주쳤던 오류를 해결한 경험

### personal reviews about the project
    팀원에게서 공유받은 .pem 키와 퍼블릭 ip 주소로 ec2 접속을 시도하였으나 실패했다. 3시간 전에는 동일한 정보로 잘 접속이 되었던 상태였기 때문에, 이전에 접속한 시간 이후로 변경된 것이나 접속을 시도한 장소(연결된 인터넷)가 바뀐 것 2개 중 하나가 문제일 것이라고 생각했다. 공공장소에서는 접속을 막았을 수도 있다 하여 집에서 다시 시도하였으나, 동일한 오류로 접속되지 않았다. 
    오류를 해결하는 과정에서 .pem 키의 사용 권한을 모두 없애고, 현재 사용자 사용하도록 하였는데, 이 부분이 잘못된 것 같아 다시 .pem 키를 저장하였고, 그 후에야 제대로 접속할 수 있었다. 정확한 오류 원인을 확인하지 못한 것은 아쉬웠지만, 몇시간 만에 잘 되던 것이 안되는 경험을 하며 '내가 지금 뭘 하고 있는지를 잘 알고 있어야겠다!'라는 생각을 다시 한번 하게 되었다. 
    icacls .\key.pem ; 해당 .pem 키 사용 권한을 가진 사용자를 보여줌.
    $env:USERNAME ; 현재 사용자 이름 보여줌. (e.g.) ybigta)
    icacls .\key.pem /grant:r "$($env:USERNAME):(R)" ; 현재 사용자에게 읽기 권한을 부여.
    icacls .\key.pem /grant:r "ybigta:(R)" ; ybigta 사용자에게 key.pem 키 사용 권한 부여. 

* 프로젝트를 진행하면서 데이터베이스 URL, 비밀번호, API 키 등과 같은 민감한 정보를 안전하게 관리하기 위해 .env 파일을 적극 활용했다.
  특히 로컬 개발 환경과 배포 환경이 분리되어 있었기 때문에, 각각에 맞는 환경변수를 별도로 관리할 수 있다는 점이 매우 효율적이었고, 이를 통해 코드 내에 민감 정보가 하드코딩 되는 것을 방지할 수 있었다.
  그러나 처음에는 .env 파일과 환경변수 관리가 생각보다 훨씬 까다롭고 복잡하다는 것을 크게 느꼈다. AWS EC2, RDS, MongoDB Atlas 등 다양한 서비스와 인프라를 연동하면서, 각각의 접속 정보(MONGO_URL, RDS_HOST, RDS_PORT 등)를 .env에 정의하는 것은 비교적 쉽지만, 이를 실제 서버와 컨테이너에 반영하는 과정에서 여러 어려움에 직면했다.
  
  가장 먼저 마주친 문제는 .env 파일이 서버에 정상적으로 올라가지 않거나, 혹은 컨테이너 내부에 환경변수가 올바르게 전달되지 않는 점이었다. 초기 Docker 이미지를 빌드하고 배포할 때 .env 파일을 복사하지 않거나, GitHub Actions 등의 CI/CD 자동화 과정에서 환경변수를 제대로 주입하지 않아서 애플리케이션이 데이터베이스에 연결하지 못하는 일이 빈번했다. 이 문제를 해결하기 위해 Dockerfile과 docker-compose, 그리고 CI/CD 워크플로우에서 .env를 안전하고 확실하게 전달하는 방법을 반복적으로 수정하고 테스트하는 과정이 필요했다.
  
  또한, AWS RDS 보안 그룹과 VPC 설정과도 밀접한 연관이 있었다. 특히 보안을 위해 RDS 퍼블릭 액세스를 허용하지 않고, VPC 내부 네트워크에서만 접근 가능하도록 설정했기 때문에, .env 파일에 기입한 RDS 호스트 주소가 퍼블릭 도메인 주소가 아닌 VPC 내부 프라이빗 IP 주소여야 했다. 초기에 퍼블릭 도메인 주소를 넣어 연결 오류가 발생했고, 문제 원인을 찾기까지 시간이 걸렸다. 결국 네트워크 구조와 보안 정책을 이해하고 .env 값을 내부 IP로 바꾸면서 문제를 해결할 수 있었다. 뿐만 아니라, URI 내 사용자명이나 비밀번호에 특수문자가 포함된 경우, 반드시 URL 인코딩을 적용해야만 정상적으로 연결된다는 점도 직접 경험하며 깨달았다.
  
  이러한 경험을 통해 .env 설정은 단순히 파일 하나를 작성하는 일이 아니라, 서버, 컨테이너, 네트워크, 보안 설정과 연동되어 복합적으로 작동하는 요소임을 몸소 느꼈다.
  그리고 배포 자동화 과정에서 환경변수를 안전하게 관리하고 주입하는 것은 보안과 안정성 측면에서 필수적인 작업이라는 것도 알게 되었다.




import os
import time
import csv
import re
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from review_analysis.crawling.base_crawler import BaseCrawler
from selenium.common.exceptions import NoSuchElementException

class KakaoCrawler(BaseCrawler):
    def __init__(self, output_dir: str):
        super().__init__(output_dir)
        self.base_url = "https://map.kakao.com/place/1890778114#comment"
        self.reviews = []
        self.driver = None

    def start_browser(self):
        options = Options()
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-features=GCM')  # GCM 에러 제거용
        self.driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()),
            options=options
        )

    def scroll_down(self):
        interval = 1
        prev_height = self.driver.execute_script("return document.body.scrollHeight")
        while True:
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight)")
            time.sleep(interval)
            curr_height = self.driver.execute_script("return document.body.scrollHeight")
            if curr_height == prev_height:
                break
            prev_height = curr_height

    def more_review(self):
        while True:
            more_buttons = self.driver.find_elements(By.CSS_SELECTOR, "span.btn_more")
            if more_buttons:
            # 강제 클릭
                self.driver.execute_script("arguments[0].click();", more_buttons[0])
                time.sleep(1)  # 클릭 후 약간 기다리기
            else:
                print("❌ '더보기' 버튼이 없습니다.")
            
            if not more_buttons:
                break

            clicked = False
            for button in more_buttons:
                try:
                    if button.text.strip() == "더보기":
                        self.driver.execute_script("arguments[0].click();", button)
                        time.sleep(0.5)
                        clicked = True
                except Exception:
                    continue

            if not clicked:
                # 더이상 "더보기" 버튼이 없으면 중단
                break
    def scrape_reviews(self):
        self.start_browser()
        self.driver.get(self.base_url)
        time.sleep(5)

    # 페이지 전체 스크롤 다운
        for _ in range(2):
            self.scroll_down()

        # 리뷰 "더보기" 버튼 모두 클릭
        self.more_review()

        # 리뷰 수집 시작
        print("[INFO] 리뷰 수집 시작")

        self.reviews = []
        empty_rounds = 0
        max_attempts = 3

        while len(self.reviews) < 500:
            comments = self.driver.find_elements(By.CSS_SELECTOR, "div.group_review > ul > li")

            print("self.reviews==",len(self.reviews))
            print("총 리뷰 수는", len(comments), "개입니다.")
            print(f"[INFO] 수집된 리뷰 수: {len(self.reviews)} / 현재 페이지 리뷰 {len(comments)}")

            if not comments:
                empty_rounds += 1
                if empty_rounds >= max_attempts:
                    print("[INFO] 더 이상 리뷰 없음 (중단)")
                    break
                time.sleep(1)
                continue

            for comment in comments:
                try:
                    date = comment.find_element(By.CSS_SELECTOR, "div.info_grade > span.txt_date").text.strip()

                    try:
                        rate = ""
                        span_els = comment.find_elements(By.CSS_SELECTOR, "span.screen_out")
                        for span in span_els:
                            text = span.get_attribute("innerText").strip()  # get_attribute로 추출
                            if re.fullmatch(r"\d+(\.\d+)?", text):  # 정수 또는 소수 체크 (예: 4, 4.0)
                                rate = text
                                break
                    except Exception as e:
                        print("[WARN] rate 추출 실패:", e)
                        rate = ""

                    try:
                        content = comment.find_element(By.CSS_SELECTOR, "div.wrap_review > a > p").text.strip()
                    except NoSuchElementException:
                        content = ""

                    self.reviews.append({
                        "rate": rate,
                        "date": date,
                        "content": content
                    })

                except Exception as e:
                    print("[ERROR] 리뷰 파싱 실패:", e)
                    continue
            break  # 현재는 첫 페이지만 사용 → 여러 페이지 수집 시 루프 구조 확장 필요

        self.driver.quit()
        print("[INFO] 브라우저 종료 및 크롤링 완료")


    def save_to_database(self):
        os.makedirs(self.output_dir, exist_ok=True)
        save_path = os.path.join(self.output_dir, "reviews_kakaomap.csv")

        with open(save_path, mode="w", newline="", encoding="utf-8-sig") as f:
            writer = csv.DictWriter(f, fieldnames=['index', 'rate', 'date', 'content'])
            writer.writeheader()
            for idx, review in enumerate(self.reviews, start=1):
                writer.writerow({
                    "index": idx,
                    "rate": review['rate'],
                    "date": review['date'],
                    "content": review['content']
                })
        print(f"[INFO] {len(self.reviews)}개 리뷰 저장 완료: {save_path}")

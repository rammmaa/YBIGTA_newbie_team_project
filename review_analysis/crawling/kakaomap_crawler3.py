import os
import time
import csv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from review_analysis.crawling.base_crawler import BaseCrawler

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
            more_buttons = self.driver.find_elements(By.CSS_SELECTOR, "span.btn_more_review")
            if not more_buttons:
                break
            for button in more_buttons:
                try:
                    self.driver.execute_script("arguments[0].click();", button)
                    time.sleep(0.5)
                except Exception:
                    continue

    def scrape_reviews(self):
        self.start_browser()
        self.driver.get(self.base_url)
        time.sleep(5)

        # iframe 전환 (카카오맵 리뷰 영역은 iframe 안에 있음)
        try:
            self.driver.switch_to.frame("entryIframe")
        except Exception:
            print("[ERROR] iframe 전환 실패")
            self.driver.quit()
            return

        # 스크롤 다운 반복
        for _ in range(2):
            self.scroll_down()

        # 더보기 버튼 눌러서 리뷰 더 불러오기
        self.more_review()

        # 리뷰 수집
        empty_rounds = 0
        max_attempts = 3

        while len(self.reviews) < 500:
            comments = self.driver.find_elements(By.CSS_SELECTOR, 'ul.list_evaluation > li')
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
                    rate = comment.find_element(By.CSS_SELECTOR, "span.star_rank > span").text.strip()
                    date = comment.find_element(By.CSS_SELECTOR, "span.txt_date").text.strip()
                    content = comment.find_element(By.CSS_SELECTOR, "p.desc_review").text.strip()

                    self.reviews.append({
                        "rate": rate,
                        "date": date,
                        "content": content
                    })

                    if len(self.reviews) >= 500:
                        break

                except Exception as e:
                    continue

            break  # 현재는 1페이지만, 필요 시 루프 구조 변경 가능

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

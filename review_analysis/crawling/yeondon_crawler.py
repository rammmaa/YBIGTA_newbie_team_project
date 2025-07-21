from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time
import os
import csv

from review_analysis.crawling.base_crawler import BaseCrawler

class YeondonCrawler(BaseCrawler):
    def __init__(self, output_dir: str):
        super().__init__(output_dir)
        self.base_url = 'https://www.google.com/maps/place/%EC%97%B0%EB%8F%88/data=!3m1!4b1!4m6!3m5!1s0x350c5bc3e1cdc0bd:0x22be2eedc74c07a4!8m2!3d33.2588769!4d126.4061366!16s%2Fg%2F11fqbws0mp?entry=ttu&g_ep=EgoyMDI1MDcxNi4wIKXMDSoASAFQAw%3D%3D'
        self.driver = None
        self.reviews = []

    def start_browser(self):
        chrome_options = Options()
        # chrome_options.add_argument('--headless')  # 필요시 주석 해제
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=chrome_options)
        self.driver.get(self.base_url)
        time.sleep(5)  # 페이지 로딩 대기
        # 리뷰 탭 클릭 시도
        try:
            review_tab = self.driver.find_element(By.CSS_SELECTOR, 'button[aria-label*="리뷰"]')
            review_tab.click()
            time.sleep(8)  # 리뷰 탭 클릭 후 충분히 대기
        except Exception as e:
            print('리뷰 탭 클릭 실패(이미 리뷰 탭일 수 있음):', e)

    def expand_all_more_buttons(self):
        # '자세히' 버튼이 없어질 때까지 반복 클릭
        while True:
            more_buttons = self.driver.find_elements(By.CSS_SELECTOR, 'button.w8nwRe.kyuRq[aria-label="자세히"]')
            if not more_buttons:
                break
            for btn in more_buttons:
                try:
                    self.driver.execute_script("arguments[0].click();", btn)
                    time.sleep(0.5)
                except Exception:
                    pass

    def scroll_and_collect_reviews(self, max_reviews=500, max_scroll=500):
        collected = set()
        last_count = 0
        try:
            scrollable = self.driver.find_element(By.CSS_SELECTOR, 'div.m6QErb.DxyBCb.kA9KIf.dS8AEf.XiKgde')
        except Exception:
            scrollable = self.driver.find_element(By.TAG_NAME, 'body')
        for i in range(max_scroll):
            # 스크롤 내리기 (리뷰 리스트 div에 직접)
            self.driver.execute_script('arguments[0].scrollTop = arguments[0].scrollHeight', scrollable)
            time.sleep(4)
            # '자세히' 버튼 모두 클릭(없어질 때까지 반복)
            self.expand_all_more_buttons()
            # 리뷰 컨테이너 다시 수집
            review_blocks = self.driver.find_elements(By.CSS_SELECTOR, 'div.jftiEf.fontBodyMedium')
            for block in review_blocks:
                try:
                    date = block.find_element(By.CSS_SELECTOR, 'span.rsqaWe').text
                    star_elem = block.find_element(By.CSS_SELECTOR, 'span.kvMYJc[role="img"]')
                    star_text = star_elem.get_attribute('aria-label')
                    rating = None
                    if star_text:
                        import re
                        m = re.search(r'별표 (\\d+)', star_text)
                        if m:
                            rating = int(m.group(1))
                    # 리뷰 본문 전체 div에서 innerText 추출
                    text_elem = block.find_element(By.CSS_SELECTOR, 'div.MyEned')
                    text = text_elem.get_attribute('innerText')
                    # '자세히'가 남아있으면 저장하지 않음
                    if '자세히' in text:
                        continue
                    key = f"{date}|{rating}|{text}"
                    if key not in collected:
                        self.reviews.append({
                            'date': date,
                            'rating': rating,
                            'text': text
                        })
                        collected.add(key)
                except Exception:
                    pass
            if len(collected) == last_count:
                break
            last_count = len(collected)
            if len(collected) >= max_reviews:
                break
        print(f"리뷰 {len(collected)}개 수집 완료")

    def scrape_reviews(self, max_reviews=500):
        self.start_browser()
        time.sleep(2)
        self.scroll_and_collect_reviews(max_reviews=max_reviews, max_scroll=100)
        self.driver.quit()

    def save_to_database(self):
        if not self.reviews:
            print('저장할 리뷰가 없습니다.')
            return
        os.makedirs(self.output_dir, exist_ok=True)
        output_path = os.path.join(self.output_dir, 'reviews_google_yeondon.csv')
        with open(output_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=['date', 'rating', 'text'])
            writer.writeheader()
            for review in self.reviews:
                writer.writerow(review)
        print(f'리뷰 {len(self.reviews)}개를 저장했습니다: {output_path}')

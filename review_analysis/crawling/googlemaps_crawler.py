from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time
import os
import csv
import re
from datetime import datetime, timedelta

from review_analysis.crawling.base_crawler import BaseCrawler
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class GooglemapsCrawler(BaseCrawler):
    def __init__(self, output_dir: str):
        super().__init__(output_dir)
        self.base_url = 'https://www.google.co.kr/maps/place/%EC%97%B0%EB%8F%88/data=!3m1!4b1!4m6!3m5!1s0x350c5bc3e1cdc0bd:0x22be2eedc74c07a4!8m2!3d33.2588769!4d126.4061366!16s%2Fg%2F11fqbws0mp?entry=ttu&g_ep=EgoyMDI1MDcyMS4wIKXMDSoASAFQAw%3D%3D'
        self.driver = None
        self.reviews = []

    def start_browser(self):
        options = Options()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=options)
        self.driver.get(self.base_url)
        wait = WebDriverWait(self.driver, 15)
        try:
            review_tab = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'button[aria-label*="리뷰"]')))
            review_tab.click()
            wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'div.jftiEf.fontBodyMedium')))
        except Exception:
            pass

    def parse_relative_date(self, date_str, base_date=None):
        if base_date is None:
            base_date = datetime.now()
        date_str = date_str.strip()
        patterns = [
            (r'(\d+)년 전', lambda n: base_date.replace(year=base_date.year - n)),
            (r'(\d+)달 전', lambda n: (base_date.replace(day=1) - timedelta(days=30*n))),
            (r'(\d+)주 전', lambda n: base_date - timedelta(weeks=n)),
            (r'(\d+)일 전', lambda n: base_date - timedelta(days=n)),
            (r'(\d+)시간 전', lambda n: base_date - timedelta(hours=n)),
            (r'(\d+)분 전', lambda n: base_date - timedelta(minutes=n)),
            (r'(\d{4}\.\d{2}\.\d{2})', lambda _: date_str)
        ]
        for pattern, func in patterns:
            m = re.match(pattern, date_str)
            if m:
                try:
                    n = int(m.group(1)) if len(m.groups()) > 0 else None
                    return func(n).strftime('%Y.%m.%d') if callable(func) else func
                except Exception:
                    return date_str
        return date_str

    def scroll_and_collect_reviews(self, max_reviews=500, max_scroll=300):
        collected = set()
        wait = WebDriverWait(self.driver, 10)
        try:
            scrollable = self.driver.find_element(By.CSS_SELECTOR, 'div.m6QErb.DxyBCb.kA9KIf.dS8AEf.XiKgde')
        except Exception:
            scrollable = self.driver.find_element(By.TAG_NAME, 'body')

        for _ in range(max_scroll):
            self.driver.execute_script('arguments[0].scrollTop = arguments[0].scrollHeight', scrollable)
            try:
                review_blocks = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'div.jftiEf.fontBodyMedium')))
            except Exception:
                review_blocks = []
            for block in review_blocks:
                try:
                    date_raw = wait.until(lambda d: block.find_element(By.CSS_SELECTOR, 'span.rsqaWe')).text
                    date = self.parse_relative_date(date_raw)
                    star_elem = wait.until(lambda d: block.find_element(By.CSS_SELECTOR, 'span.kvMYJc[role="img"]'))
                    star_text = star_elem.get_attribute('aria-label')
                    rating = int(re.search(r'별표 (\d+)', star_text).group(1)) if star_text else None
                    try:
                        more_btn = block.find_element(By.CSS_SELECTOR, 'button.w8nwRe.kyuRq[aria-label="더보기"]')
                        wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'button.w8nwRe.kyuRq[aria-label="더보기"]')))
                        self.driver.execute_script("arguments[0].click();", more_btn)
                        wait.until(lambda d: block.find_element(By.CSS_SELECTOR, 'span.wiI7pd').get_attribute('innerText'))
                    except Exception:
                        pass
                    text_elem = wait.until(lambda d: block.find_element(By.CSS_SELECTOR, 'span.wiI7pd'))
                    text = text_elem.get_attribute('innerText')
                    key = f"{date}|{rating}|{text}"
                    if key not in collected:
                        self.reviews.append({'date': date, 'rating': rating, 'text': text})
                        collected.add(key)
                        if len(collected) % 50 == 0:
                            print(f"{len(collected)}개 리뷰 수집됨")
                except Exception as e:
                    print(f"리뷰 파싱 에러: {e}")
                if len(collected) >= max_reviews:
                    return

    def scrape_reviews(self, max_reviews=500):
        try:
            self.start_browser()
            time.sleep(2)
            self.scroll_and_collect_reviews(max_reviews=max_reviews, max_scroll=300)
        except Exception as e:
            print(f"크롤링 중 오류: {e}")
        finally:
            if self.driver:
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

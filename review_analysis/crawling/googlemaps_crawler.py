from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time
import os
import csv
import re
from review_analysis.crawling.base_crawler import BaseCrawler

class GoogleMapsCrawler(BaseCrawler):
    """구글 지도 리뷰를 크롤링하는 Crawler 클래스."""
    def __init__(self, output_dir: str):
        """output_dir는 무시하고 항상 output 폴더에 저장."""
        super().__init__('output')
        self.base_url = 'https://www.google.com/maps/place/%EC%97%B0%EB%8F%88/data=!3m1!4b1!4m6!3m5!1s0x350c5bc3e1cdc0bd:0x22be2eedc74c07a4!8m2!3d33.2588769!4d126.4061366!16s%2Fg%2F11fqbws0mp?entry=ttu&g_ep=EgoyMDI1MDcxNi4wIKXMDSoASAFQAw%3D%3D'
        self.driver = None
        self.reviews = []

    def start_browser(self):
        """크롬 브라우저를 실행하고 리뷰 탭으로 이동."""
        chrome_options = Options()
        chrome_options.add_argument('--headless')  # 필요시 주석 해제
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=chrome_options)
        self.driver.get(self.base_url)
        time.sleep(0.2)

        review_tab = self.driver.find_element(By.CSS_SELECTOR, 'button[aria-label*="리뷰"]')
        review_tab.click()
        time.sleep(0.2)


    def scroll_and_collect_reviews(self, max_reviews=500, max_scroll=500):
        """스크롤을 내리며 리뷰를 최대 max_reviews개까지 수집."""
        collected = set()
        try:
            scrollable = self.driver.find_element(By.CSS_SELECTOR, 'div.m6QErb.DxyBCb.kA9KIf.dS8AEf.XiKgde')
        except Exception:
            scrollable = self.driver.find_element(By.TAG_NAME, 'body')
        for i in range(max_scroll):
            self.driver.execute_script('arguments[0].scrollTop = arguments[0].scrollHeight', scrollable)
            time.sleep(0.1)
            review_blocks = self.driver.find_elements(By.CSS_SELECTOR, 'div.jftiEf.fontBodyMedium')
            for block in review_blocks:
                try:
                    review_id = block.get_attribute('data-review-id')
                    if not review_id:
                        continue
                    try:
                        date = block.find_element(By.CSS_SELECTOR, 'span.rsqaWe').text
                        if date.startswith('수정일:'):
                            date = date.replace('수정일:', '').strip()
                    except Exception:
                        date = '알수없음'
                    star_elem = block.find_element(By.CSS_SELECTOR, 'span.kvMYJc[role="img"]')
                    star_text = star_elem.get_attribute('aria-label')
                    rating = None
                    if star_text:
                        m = re.search(r'별표 (\d+)', star_text)
                        if m:
                            rating = int(m.group(1))
                    try:
                        more_btn = block.find_element(By.CSS_SELECTOR, 'button.w8nwRe.kyuRq[aria-label="더보기"]')
                        self.driver.execute_script("arguments[0].click();", more_btn)
                        time.sleep(0.05)
                    except Exception:
                        pass
                    text_elem = block.find_element(By.CSS_SELECTOR, 'span.wiI7pd')
                    text = text_elem.get_attribute('innerText')
                    key = review_id
                    if key not in collected:
                        self.reviews.append({
                            'date': date,
                            'rating': rating,
                            'text': text
                        })
                        collected.add(key)
                except Exception as e:
                    print(f'리뷰 파싱 오류: {e}')
                if len(collected) >= max_reviews:
                    break

    def scrape_reviews(self, max_reviews=500):
        """크롤링 전체 실행."""
        print('크롤링 시작!')
        self.start_browser()
        time.sleep(2)
        self.scroll_and_collect_reviews(max_reviews=max_reviews, max_scroll=500)
        self.driver.quit()
        print('크롤링 종료!')

    def save_to_database(self):
        """수집한 리뷰를 output/review_googlemaps.csv로 저장."""
        if not self.reviews:
            print('저장할 리뷰가 없습니다.')
            return
        os.makedirs('output', exist_ok=True)
        output_path = os.path.join('output', 'review_googlemaps.csv')
        with open(output_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=['date', 'rating', 'text'])
            writer.writeheader()
            for review in self.reviews:
                writer.writerow(review)
        print(f'리뷰 {len(self.reviews)}개를 저장했습니다: {output_path}') 
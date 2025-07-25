from review_analysis.crawling.base_crawler import BaseCrawler
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import os
import time
import csv

class CatchTableCrawler(BaseCrawler):
    def __init__(self, output_dir: str):
        super().__init__(output_dir)
        self.base_url = 'https://app.catchtable.co.kr/ct/shop/yeondon_/review'
        self.driver = None
        self.reviews : list[dict[str, str]] = []
        
    def start_browser(self):
        options = Options()
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        return driver
    
    def scrape_reviews(self):
        driver = self.start_browser()
        driver.get(self.base_url)
        time.sleep(5)
        last_index = 0
        
        while len(self.reviews) < 500:
                review_articles = driver.find_elements(By.CSS_SELECTOR, "article.__my-review-post")
                new_articles = review_articles[last_index:]
                for article in new_articles:
                    try:
                        rating_el = article.find_element(By.CSS_SELECTOR, "div._10fm75h6")
                        rating = rating_el.text.strip()

                        date_el = article.find_element(By.CSS_SELECTOR, "span.__date")
                        date = date_el.text.strip()

                        content_el = article.find_element(By.CSS_SELECTOR, "p.review-content")
                        content = content_el.text.strip()

                        self.reviews.append({"rating": rating, "date": date, "content": content})
                        print(f"[{len(self.reviews)}] {date} | {rating}점 | {content[:30]}...")

                    except Exception as e:
                        continue  

                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(1.5) 

        driver.quit()
    
    def save_to_database(self):
        os.makedirs(self.output_dir, exist_ok=True)
        output_path = os.path.join(self.output_dir, "reviews_catchtable.csv")

        with open(output_path, mode="w", newline="", encoding="utf-8-sig") as f:
            writer = csv.DictWriter(f, fieldnames=["index", "rating", "date", "content"])
            writer.writeheader()
            for idx, review in enumerate(self.reviews, start=1): 
                writer.writerow({
                    "index": idx,
                    "rating": review["rating"],
                    "date": review["date"],
                    "content": review["content"]
                })
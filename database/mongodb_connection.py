from pymongo import MongoClient
from dotenv import load_dotenv
import os

load_dotenv()

mongo_url = os.getenv("MONGO_URL")

mongo_client = MongoClient(mongo_url)

# 데이터베이스 이름을 명시적으로 지정
mongo_db = mongo_client.get_database("assignment")


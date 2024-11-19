from dotenv import load_dotenv
import os

load_dotenv()

BASE_URL = os.getenv("BASE_URL")
CATEGORIES = os.getenv("CATEGORIES")

TIMEOUT = os.getenv("TIMEOUT")
DELAY = os.getenv("DELAY")
MAX_RETRIES = os.getenv("MAX_RETRIES")
MAX_WORKERS = os.getenv("MAX_WORKERS")
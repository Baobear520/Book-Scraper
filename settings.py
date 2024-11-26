from dotenv import load_dotenv
import os

load_dotenv()

BASE_URL = os.getenv("BASE_URL")
CATEGORIES = os.getenv("CATEGORIES")

TIMEOUT = int(os.getenv("TIMEOUT"))
DELAY = int(os.getenv("DELAY"))
MAX_RETRIES = int(os.getenv("MAX_RETRIES"))
MAX_WORKERS = int(os.getenv("MAX_WORKERS"))


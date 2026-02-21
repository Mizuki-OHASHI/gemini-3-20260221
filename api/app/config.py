import os
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.environ["GEMINI_API_KEY"]
FIREBASE_STORAGE_BUCKET = os.environ["FIREBASE_STORAGE_BUCKET"]

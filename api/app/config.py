import os
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.environ["GEMINI_API_KEY"]
FIREBASE_STORAGE_BUCKET = os.environ["FIREBASE_STORAGE_BUCKET"]

NANOBANANA_API_URL = os.environ["NANOBANANA_API_URL"]
NANOBANANA_API_KEY = os.getenv("NANOBANANA_API_KEY", "")

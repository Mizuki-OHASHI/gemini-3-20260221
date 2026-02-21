import os
import firebase_admin
from firebase_admin import credentials, firestore, storage
from app.config import FIREBASE_STORAGE_BUCKET

opts = {"storageBucket": FIREBASE_STORAGE_BUCKET}

key_path = os.getenv("FIREBASE_SERVICE_ACCOUNT_KEY")
if key_path and os.path.exists(key_path):
    # ローカル: serviceAccountKey.json を使用
    cred = credentials.Certificate(key_path)
    firebase_admin.initialize_app(cred, opts)
else:
    # Cloud Run: デフォルト認証
    firebase_admin.initialize_app(options=opts)

db = firestore.client()
bucket = storage.bucket()

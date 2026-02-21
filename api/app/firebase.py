import firebase_admin
from firebase_admin import credentials, firestore, storage
from app.config import FIREBASE_SERVICE_ACCOUNT_KEY, FIREBASE_STORAGE_BUCKET

cred = credentials.Certificate(FIREBASE_SERVICE_ACCOUNT_KEY)
firebase_admin.initialize_app(cred, {"storageBucket": FIREBASE_STORAGE_BUCKET})

db = firestore.client()
bucket = storage.bucket()

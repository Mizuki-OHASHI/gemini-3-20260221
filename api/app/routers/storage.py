from fastapi import APIRouter, UploadFile

from app.firebase import bucket

router = APIRouter(prefix="/storage", tags=["storage"])


@router.post("/upload")
async def upload_file(file: UploadFile):
    blob = bucket.blob(f"uploads/{file.filename}")
    blob.upload_from_file(file.file, content_type=file.content_type)
    blob.make_public()
    return {"url": blob.public_url, "path": blob.name}


@router.get("/url/{path:path}")
async def get_signed_url(path: str):
    import datetime

    blob = bucket.blob(path)
    url = blob.generate_signed_url(expiration=datetime.timedelta(hours=1))
    return {"url": url}

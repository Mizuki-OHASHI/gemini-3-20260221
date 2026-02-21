from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException, UploadFile
from google.genai import types

from app.firebase import bucket, db
from app.gemini import client
from app.scenario import load_hint_messages
from app.schemas import PhotoListResponse, PhotoResponse

router = APIRouter(prefix="/game/{game_id}/photos", tags=["photo"])


@router.post("/", response_model=PhotoResponse)
async def upload_photo(game_id: str, file: UploadFile):
    # Verify game exists
    game_doc = db.collection("games").document(game_id).get()
    if not game_doc.exists:
        raise HTTPException(status_code=404, detail="Game not found")

    game_data = game_doc.to_dict()
    photo_count = game_data.get("photo_count", 0) + 1

    # Upload to GCS
    seq = f"{photo_count:03d}"
    gcs_path = f"games/{game_id}/photos/{seq}_original.jpg"
    blob = bucket.blob(gcs_path)
    blob.upload_from_file(file.file, content_type=file.content_type or "image/jpeg")
    blob.make_public()

    now = datetime.now(timezone.utc)

    # Save to Firestore
    photo_ref = db.collection("photos").document()
    photo_data = {
        "game_id": game_id,
        "original_path": gcs_path,
        "original_url": blob.public_url,
        "ghost_path": None,
        "ghost_url": None,
        "ghost_gesture": None,
        "ghost_message": None,
        "created_at": now,
    }
    photo_ref.set(photo_data)

    # Update game photo count
    db.collection("games").document(game_id).update(
        {"photo_count": photo_count, "updated_at": now}
    )

    return PhotoResponse(
        id=photo_ref.id,
        game_id=game_id,
        original_url=blob.public_url,
        created_at=now,
    )


@router.get("/", response_model=PhotoListResponse)
async def list_photos(game_id: str):
    docs = (
        db.collection("photos")
        .where("game_id", "==", game_id)
        .order_by("created_at")
        .stream()
    )
    photos = []
    for doc in docs:
        d = doc.to_dict()
        photos.append(
            PhotoResponse(
                id=doc.id,
                game_id=d["game_id"],
                original_url=d["original_url"],
                ghost_url=d.get("ghost_url"),
                ghost_gesture=d.get("ghost_gesture"),
                ghost_message=d.get("ghost_message"),
                detected_item=d.get("detected_item"),
                created_at=d["created_at"],
            )
        )
    return PhotoListResponse(photos=photos)


@router.get("/{photo_id}", response_model=PhotoResponse)
async def get_photo(game_id: str, photo_id: str):
    doc = db.collection("photos").document(photo_id).get()
    if not doc.exists:
        raise HTTPException(status_code=404, detail="Photo not found")
    d = doc.to_dict()
    if d["game_id"] != game_id:
        raise HTTPException(status_code=404, detail="Photo not found")
    return PhotoResponse(
        id=doc.id,
        game_id=d["game_id"],
        original_url=d["original_url"],
        ghost_url=d.get("ghost_url"),
        ghost_gesture=d.get("ghost_gesture"),
        ghost_message=d.get("ghost_message"),
        detected_item=d.get("detected_item"),
        created_at=d["created_at"],
    )


@router.post("/{photo_id}/ghost", response_model=PhotoResponse)
async def generate_ghost(game_id: str, photo_id: str):
    # Get photo
    photo_doc = db.collection("photos").document(photo_id).get()
    if not photo_doc.exists:
        raise HTTPException(status_code=404, detail="Photo not found")
    photo_data = photo_doc.to_dict()
    if photo_data["game_id"] != game_id:
        raise HTTPException(status_code=404, detail="Photo not found")

    # Get game data for ghost description
    game_doc = db.collection("games").document(game_id).get()
    if not game_doc.exists:
        raise HTTPException(status_code=404, detail="Game not found")
    game_data = game_doc.to_dict()
    avatar_url: str | None = game_data.get("avatar_url")

    # Get hint messages
    hint_messages = load_hint_messages()

    if avatar_url:
        appearance = "添付のアバター画像の人物を幽霊として合成してください。"
    else:
        ghost_description = game_data.get(
            "ghost_description",
            "長い黒髪の少女の幽霊。白いワンピースを着て、悲しげな表情をしている。",
        )
        appearance = f"幽霊の外見: {ghost_description}"

    ghost_prompt = f"""この写真に幽霊を合成してください。
{appearance}
幽霊の行動: 幽霊はただ泣いている。悲しげに佇んでいる
元の写真の構図や雰囲気を保持したまま、半透明の幽霊を自然に重ねてください。"""

    # Generate ghost image via Gemini
    contents: list[types.Part] = []
    if avatar_url:
        avatar_blob_name = avatar_url.split(f"/{bucket.name}/")[-1]
        avatar_blob = bucket.blob(avatar_blob_name)
        avatar_bytes = avatar_blob.download_as_bytes()
        contents.append(types.Part.from_bytes(data=avatar_bytes, mime_type="image/png"))

    # 元の写真を取得して添付
    original_blob = bucket.blob(photo_data["original_path"])
    original_bytes = original_blob.download_as_bytes()
    contents.append(types.Part.from_bytes(data=original_bytes, mime_type="image/jpeg"))
    contents.append(types.Part.from_text(text=ghost_prompt))

    response = await client.aio.models.generate_content(
        model="gemini-2.0-flash-exp-image-generation",
        contents=contents,
        config=types.GenerateContentConfig(
            response_modalities=["IMAGE", "TEXT"],
        ),
    )

    ghost_image_data = None
    ghost_mime_type = "image/jpeg"
    ghost_message = None

    for part in response.candidates[0].content.parts:
        if part.inline_data:
            ghost_image_data = part.inline_data.data
            ghost_mime_type = part.inline_data.mime_type
        elif part.text:
            ghost_message = part.text

    if not ghost_image_data:
        raise HTTPException(status_code=500, detail="Failed to generate ghost image")

    # Upload ghost image to GCS
    original_path = photo_data["original_path"]
    ghost_path = original_path.replace("_original.", "_ghost.")
    blob = bucket.blob(ghost_path)
    blob.upload_from_string(ghost_image_data, content_type=ghost_mime_type)
    blob.make_public()

    now = datetime.now(timezone.utc)

    # Update Firestore
    update_data = {
        "ghost_path": ghost_path,
        "ghost_url": blob.public_url,
        "ghost_gesture": hint_messages.get("none", ""),
        "ghost_message": ghost_message,
    }
    db.collection("photos").document(photo_id).update(update_data)
    db.collection("games").document(game_id).update({"updated_at": now})

    return PhotoResponse(
        id=photo_id,
        game_id=game_id,
        original_url=photo_data["original_url"],
        ghost_url=blob.public_url,
        ghost_gesture=hint_messages.get("none", ""),
        ghost_message=ghost_message,
        created_at=photo_data["created_at"],
    )

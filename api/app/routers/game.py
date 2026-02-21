import logging
from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException
from google.genai import types

from app.firebase import bucket, db
from app.gemini import client
from app.schemas import (
    AvatarResponse,
    GameCreateRequest,
    GameResponse,
    GameUpdateRequest,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/game", tags=["game"])


@router.post("/", response_model=GameResponse)
async def create_game(req: GameCreateRequest):
    now = datetime.now(timezone.utc)
    doc_ref = db.collection("games").document()
    data = {
        "player_name": req.player_name,
        "status": "waiting",
        "photo_count": 0,
        "ghost_description": req.ghost_description,
        "cleared_items": [],
        "created_at": now,
        "updated_at": now,
    }
    doc_ref.set(data)
    return GameResponse(id=doc_ref.id, **data)


@router.get("/{game_id}", response_model=GameResponse)
async def get_game(game_id: str):
    doc = db.collection("games").document(game_id).get()
    if not doc.exists:
        raise HTTPException(status_code=404, detail="Game not found")
    return GameResponse(id=doc.id, **doc.to_dict())


@router.patch("/{game_id}", response_model=GameResponse)
async def update_game(game_id: str, req: GameUpdateRequest):
    doc_ref = db.collection("games").document(game_id)
    doc = doc_ref.get()
    if not doc.exists:
        raise HTTPException(status_code=404, detail="Game not found")

    updates = req.model_dump(exclude_none=True)
    if not updates:
        raise HTTPException(status_code=400, detail="No fields to update")

    updates["updated_at"] = datetime.now(timezone.utc)
    doc_ref.update(updates)

    updated_doc = doc_ref.get()
    return GameResponse(id=updated_doc.id, **updated_doc.to_dict())


@router.post("/{game_id}/avatar", response_model=AvatarResponse)
async def generate_avatar(game_id: str):
    """ghost_description からアバター画像を生成し GCS に保存する。"""
    game_ref = db.collection("games").document(game_id)
    game_doc = game_ref.get()
    if not game_doc.exists:
        raise HTTPException(status_code=404, detail="Game not found")

    game_data = game_doc.to_dict()
    ghost_description = game_data.get(
        "ghost_description",
        "長い黒髪の少女。白いワンピースを着て、悲しげな表情をしている。",
    )

    # 幽霊っぽくない普通の人物アバターとして生成するプロンプト
    avatar_prompt = f"""以下の外見の人物のポートレートイラストを描いてください。
人物の外見: {ghost_description}
スタイル: リアルな日本人で、上半身のポートレート、シンプルな背景。
注意: 幽霊や怖い要素は一切入れないでください。普通の生きている人物として描いてください。"""

    response = await client.aio.models.generate_content(
        model="nano-banana-pro-preview",
        contents=avatar_prompt,
        config=types.GenerateContentConfig(
            response_modalities=["IMAGE", "TEXT"],
        ),
    )

    avatar_image_data = None
    avatar_mime_type = "image/png"

    for part in response.candidates[0].content.parts:
        if part.inline_data:
            avatar_image_data = part.inline_data.data
            avatar_mime_type = part.inline_data.mime_type or "image/png"

    if not avatar_image_data:
        raise HTTPException(status_code=500, detail="Avatar image generation failed")

    # GCS にアップロード
    ext = "png" if "png" in avatar_mime_type else "jpg"
    gcs_path = f"games/{game_id}/avatar.{ext}"
    blob = bucket.blob(gcs_path)
    blob.upload_from_string(avatar_image_data, content_type=avatar_mime_type)
    blob.make_public()
    avatar_url = blob.public_url

    # Firestore に保存
    game_ref.update({
        "avatar_url": avatar_url,
        "updated_at": datetime.now(timezone.utc),
    })

    return AvatarResponse(game_id=game_id, avatar_url=avatar_url)

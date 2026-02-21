import json
import logging
from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException, UploadFile
from google.cloud.firestore_v1 import ArrayUnion
from google.genai import types

from app.firebase import bucket, db
from app.gemini import client
from app.scenario import load_chapters
from app.schemas import TurnResponse, VisionDetectionResult

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/game/{game_id}", tags=["turn"])

ALL_ITEMS = {"bookshelf", "clock", "mirror"}

ITEM_LABELS = {
    "bookshelf": "本棚",
    "clock": "時計",
    "mirror": "鏡",
}

# Map item -> chapter number for story lookup
ITEM_CHAPTER_MAP = {
    "bookshelf": 1,
    "clock": 2,
    "mirror": 3,
}


def _build_vision_prompt(remaining_items: list[str]) -> str:
    items_str = ", ".join(f"{item}({ITEM_LABELS[item]})" for item in remaining_items)
    return f"""あなたは写真に写っているものを判定するAIです。
残りアイテム: {items_str}
この写真に上記アイテムのどれかが写っていますか？最も確信度の高いもの1つだけ回答してください。
どれも写っていない場合は detected_item を null にしてください。

JSON形式で回答:
{{"detected_item": "アイテム名 or null", "confidence": "high/medium/low/none", "explanation": "判定理由"}}"""


def _build_ghost_prompt(ghost_description: str, ghost_prompt_template: str) -> str:
    return f"""この写真に幽霊を合成してください。
幽霊の外見: {ghost_description}
幽霊の行動: {ghost_prompt_template}
元の写真の構図や雰囲気を保持したまま、半透明の幽霊を自然に重ねてください。"""


@router.post("/turn", response_model=TurnResponse)
async def play_turn(game_id: str, file: UploadFile):
    # 1. ゲーム検証
    game_ref = db.collection("games").document(game_id)
    game_doc = game_ref.get()
    if not game_doc.exists:
        raise HTTPException(status_code=404, detail="Game not found")

    game_data = game_doc.to_dict()
    if game_data.get("status") == "solved":
        raise HTTPException(status_code=400, detail="Game already solved")

    ghost_description = game_data.get(
        "ghost_description",
        "長い黒髪の少女の幽霊。白いワンピースを着て、悲しげな表情をしている。",
    )
    cleared_items: list[str] = game_data.get("cleared_items", [])

    # 2. 残りアイテム計算
    remaining_items = sorted(ALL_ITEMS - set(cleared_items))
    if not remaining_items:
        raise HTTPException(status_code=400, detail="All items already cleared")

    # 3. 写真アップロード
    photo_bytes = await file.read()
    photo_count = game_data.get("photo_count", 0) + 1
    seq = f"{photo_count:03d}"
    gcs_path = f"games/{game_id}/photos/{seq}_original.jpg"
    blob = bucket.blob(gcs_path)
    blob.upload_from_string(photo_bytes, content_type=file.content_type or "image/jpeg")
    blob.make_public()
    original_url = blob.public_url

    now = datetime.now(timezone.utc)

    # 4. Vision 検出
    detection = await _detect_item(photo_bytes, remaining_items)

    detected_item = None
    detected_chapter = None
    ghost_url = None
    ghost_message = None
    story = None

    if detection.detected_item and detection.confidence in ("high", "medium"):
        detected_item = detection.detected_item
        detected_chapter = ITEM_CHAPTER_MAP.get(detected_item)

        # チャプターのストーリーを取得
        chapters = load_chapters()
        chapter = chapters.get(detected_chapter)
        if chapter:
            story = chapter.story
            ghost_prompt_template = chapter.ghost_prompt_template
        else:
            ghost_prompt_template = ""

        # 5. Ghost 合成
        try:
            ghost_url, ghost_message = await _generate_ghost(
                photo_bytes,
                ghost_description,
                ghost_prompt_template,
                game_id,
                seq,
            )
        except Exception:
            logger.exception("Ghost generation failed")
            # Ghost 生成失敗 → アイテム未クリア扱い
            detected_item = None
            detected_chapter = None
            story = None

    # 6. ゲーム状態更新
    update_data: dict = {
        "photo_count": photo_count,
        "updated_at": now,
    }

    if detected_item:
        cleared_items = list(set(cleared_items) | {detected_item})
        update_data["cleared_items"] = ArrayUnion([detected_item])

    new_remaining = sorted(ALL_ITEMS - set(cleared_items))
    game_solved = len(new_remaining) == 0

    if game_solved:
        update_data["status"] = "solved"

    game_ref.update(update_data)

    # 7. 写真レコード保存
    photo_ref = db.collection("photos").document()
    photo_data = {
        "game_id": game_id,
        "chapter": detected_chapter,
        "original_path": gcs_path,
        "original_url": original_url,
        "ghost_path": None,
        "ghost_url": ghost_url,
        "ghost_gesture": None,
        "ghost_message": ghost_message,
        "detected_item": detected_item,
        "created_at": now,
    }
    photo_ref.set(photo_data)

    # 8. メッセージ生成
    if game_solved:
        message = "おめでとうございます！すべてのアイテムを見つけ、幽霊の謎を解き明かしました。"
    elif detected_item:
        label = ITEM_LABELS.get(detected_item, detected_item)
        message = f"{label}を発見しました！幽霊が現れています..."
    else:
        remaining_labels = [ITEM_LABELS.get(i, i) for i in new_remaining]
        message = f"アイテムが見つかりませんでした。{', '.join(remaining_labels)}を探してみましょう。"

    return TurnResponse(
        game_id=game_id,
        photo_id=photo_ref.id,
        original_url=original_url,
        detected_item=detected_item,
        detected_chapter=detected_chapter,
        ghost_url=ghost_url,
        ghost_message=ghost_message,
        cleared_items=cleared_items,
        items_remaining=new_remaining,
        game_status="solved" if game_solved else "playing",
        game_solved=game_solved,
        story=story,
        message=message,
    )


async def _detect_item(
    photo_bytes: bytes, remaining_items: list[str]
) -> VisionDetectionResult:
    """Gemini Vision でアイテムを検出する。"""
    prompt = _build_vision_prompt(remaining_items)

    response = await client.aio.models.generate_content(
        model="gemini-2.5-flash",
        contents=[
            types.Part.from_bytes(data=photo_bytes, mime_type="image/jpeg"),
            types.Part.from_text(text=prompt),
        ],
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=VisionDetectionResult,
        ),
    )

    try:
        result = json.loads(response.text)
        # detected_item が残りアイテムに含まれない場合は未検出扱い
        if result.get("detected_item") and result["detected_item"] not in remaining_items:
            result["detected_item"] = None
            result["confidence"] = "none"
        return VisionDetectionResult(**result)
    except (json.JSONDecodeError, ValueError):
        logger.exception("Failed to parse vision detection result")
        return VisionDetectionResult(
            detected_item=None, confidence="none", explanation="Parse error"
        )


async def _generate_ghost(
    photo_bytes: bytes,
    ghost_description: str,
    ghost_prompt_template: str,
    game_id: str,
    seq: str,
) -> tuple[str, str | None]:
    """Gemini で幽霊画像を合成し、GCS にアップロードする。"""
    prompt = _build_ghost_prompt(ghost_description, ghost_prompt_template)

    response = await client.aio.models.generate_content(
        model="gemini-3-pro-image-preview",
        contents=[
            types.Part.from_bytes(data=photo_bytes, mime_type="image/jpeg"),
            types.Part.from_text(text=prompt),
        ],
        config=types.GenerateContentConfig(
            response_modalities=["TEXT", "IMAGE"],
        ),
    )

    ghost_image_data = None
    ghost_mime_type = "image/png"
    ghost_message = None

    for part in response.candidates[0].content.parts:
        if part.inline_data:
            ghost_image_data = part.inline_data.data
            ghost_mime_type = part.inline_data.mime_type or "image/png"
        elif part.text:
            ghost_message = part.text

    if not ghost_image_data:
        raise RuntimeError("Ghost image generation returned no image data")

    # GCS にアップロード
    ext = "png" if "png" in ghost_mime_type else "jpg"
    ghost_path = f"games/{game_id}/photos/{seq}_ghost.{ext}"
    blob = bucket.blob(ghost_path)
    blob.upload_from_string(ghost_image_data, content_type=ghost_mime_type)
    blob.make_public()

    return blob.public_url, ghost_message

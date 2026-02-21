import json
import logging
from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException, UploadFile
from google.cloud.firestore_v1 import ArrayUnion
from google.genai import types

from app.firebase import bucket, db
from app.gemini import client
from app.scenario import get_game_items, load_hint_messages
from app.schemas import TurnResponse, VisionDetectionResult

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/game/{game_id}", tags=["turn"])

ITEM_LABELS = {
    "cup": "コップ",
    "air_conditioner": "エアコン",
    "clock": "時計",
}


def _build_vision_prompt(remaining_items: list[str]) -> str:
    items_str = ", ".join(
        f"{item}({ITEM_LABELS.get(item, item)})" for item in remaining_items
    )
    return f"""あなたは写真に写っているものを判定するAIです。
残りアイテム: {items_str}
この写真に上記アイテムのどれかが写っていますか？最も確信度の高いもの1つだけ回答してください。
どれも写っていない場合は detected_item を null にしてください。

JSON形式で回答:
{{"detected_item": "アイテム名 or null", "confidence": "high/medium/low/none", "explanation": "判定理由"}}"""


def _build_ghost_prompt(
    hint_message: str, detected_item: str | None, has_avatar: bool
) -> str:
    if detected_item:
        action = f"幽霊は{ITEM_LABELS.get(detected_item, detected_item)}を指さしている"
    else:
        action = "幽霊はただ泣いている。悲しげに佇んでいる"
    if has_avatar:
        appearance = "添付のアバター画像の人物を幽霊として合成してください。"
    else:
        appearance = "幽霊の外見: 長い黒髪の少女の幽霊。白いワンピースを着て、悲しげな表情をしている。"
    return f"""この写真に幽霊を合成してください。
{appearance}
幽霊の行動: {action}
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

    avatar_url: str | None = game_data.get("avatar_url")
    cleared_items: list[str] = game_data.get("cleared_items", [])

    # 2. 残りアイテム計算
    all_items = get_game_items()
    remaining_items = sorted(all_items - set(cleared_items))
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

    hint_messages = load_hint_messages()
    detected_item = None
    ghost_url = None
    ghost_message = None

    if detection.detected_item and detection.confidence in ("high", "medium"):
        detected_item = detection.detected_item

    # ヒントメッセージ取得
    if detected_item:
        hint_message = hint_messages.get(detected_item, "")
    else:
        hint_message = hint_messages.get("none", "")

    # 5. Ghost 合成（常に生成）
    try:
        ghost_url, ghost_message = await _generate_ghost(
            photo_bytes,
            avatar_url,
            hint_message,
            detected_item,
            game_id,
            seq,
        )
    except Exception:
        logger.exception("Ghost generation failed")

    # 6. ゲーム状態更新
    update_data: dict = {
        "photo_count": photo_count,
        "updated_at": now,
    }

    if detected_item:
        cleared_items = list(set(cleared_items) | {detected_item})
        update_data["cleared_items"] = ArrayUnion([detected_item])

    new_remaining = sorted(all_items - set(cleared_items))
    all_cleared = len(new_remaining) == 0

    if all_cleared:
        hint_message = hint_messages.get("final", hint_message)

    game_ref.update(update_data)

    # 7. 写真レコード保存
    photo_ref = db.collection("photos").document()
    photo_data = {
        "game_id": game_id,
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
    if all_cleared:
        message = "すべての手がかりが揃いました。犯人を指名してください。"
    elif detected_item:
        label = ITEM_LABELS.get(detected_item, detected_item)
        message = f"{label}を発見しました！幽霊が何かを伝えています..."
    else:
        message = (
            f"手がかりが見つかりませんでした。ただ悲しそうに悲しそうに佇んでいます。"
        )

    return TurnResponse(
        game_id=game_id,
        photo_id=photo_ref.id,
        original_url=original_url,
        detected_item=detected_item,
        ghost_url=ghost_url,
        ghost_message=ghost_message,
        cleared_items=cleared_items,
        items_remaining=new_remaining,
        game_status="playing",
        game_solved=False,
        hint_message=hint_message,
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
        if (
            result.get("detected_item")
            and result["detected_item"] not in remaining_items
        ):
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
    avatar_url: str | None,
    hint_message: str,
    detected_item: str | None,
    game_id: str,
    seq: str,
) -> tuple[str, str | None]:
    """Gemini で幽霊画像を合成し、GCS にアップロードする。"""
    has_avatar = avatar_url is not None
    prompt = _build_ghost_prompt(hint_message, detected_item, has_avatar)

    contents: list[types.Part] = []
    if avatar_url:
        # GCS からアバター画像を取得して参照画像として添付
        avatar_blob_name = avatar_url.split(f"/{bucket.name}/")[-1]
        avatar_blob = bucket.blob(avatar_blob_name)
        avatar_bytes = avatar_blob.download_as_bytes()
        contents.append(types.Part.from_bytes(data=avatar_bytes, mime_type="image/png"))
    contents.append(types.Part.from_bytes(data=photo_bytes, mime_type="image/jpeg"))
    contents.append(types.Part.from_text(text=prompt))

    response = await client.aio.models.generate_content(
        model="gemini-3-pro-image-preview",
        contents=contents,
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

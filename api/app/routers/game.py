import json
import logging
from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException
from google.genai import types

from app.firebase import bucket, db
from app.gemini import client
from app.scenario import get_game_items, load_solution
from app.schemas import (
    AccusationJudgment,
    AccusationRequest,
    AccusationResponse,
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


@router.post("/{game_id}/accuse", response_model=AccusationResponse)
async def accuse(game_id: str, req: AccusationRequest):
    """犯人を告発し、LLMで正誤判定する。"""
    game_ref = db.collection("games").document(game_id)
    game_doc = game_ref.get()
    if not game_doc.exists:
        raise HTTPException(status_code=404, detail="Game not found")

    game_data = game_doc.to_dict()
    if game_data.get("status") == "solved":
        raise HTTPException(status_code=400, detail="Game already solved")

    cleared_items = set(game_data.get("cleared_items", []))
    all_items = get_game_items()
    if cleared_items != all_items:
        raise HTTPException(
            status_code=400,
            detail="All clues must be found before making an accusation",
        )

    solution_text = load_solution()
    judgment = await _judge_accusation(req.suspect_name, req.reason, solution_text)

    if judgment.correct:
        game_ref.update({
            "status": "solved",
            "updated_at": datetime.now(timezone.utc),
        })

    return AccusationResponse(correct=judgment.correct, message=judgment.explanation)


async def _judge_accusation(
    suspect_name: str, reason: str, solution_text: str
) -> AccusationJudgment:
    """Gemini で告発の正誤を判定する。"""
    prompt = f"""あなたはミステリーゲームの審判AIです。
プレイヤーが犯人を指名し、その理由を述べました。
正解の情報と照らし合わせて、プレイヤーの推理が正しいかどうかを判定してください。

【正解の情報】
{solution_text}

【プレイヤーの回答】
犯人: {suspect_name}
理由: {reason}

【判定基準】
1. 犯人の名前が正しいかどうか（最重要）
2. 理由については、完全一致でなくても方向性が合っていれば正解とする
3. 犯人が間違っている場合は、理由がどんなに良くても不正解とする

JSON形式で回答してください:
{{"correct": true/false, "explanation": "プレイヤーへのメッセージ（日本語、2-3文）"}}

正解の場合は「お見事です！」のようなポジティブなメッセージ、
不正解の場合は「もう一度考えてみてください」のようなヒントを含むメッセージにしてください。
犯人が不正解の場合でも、正解の犯人名は絶対に明かさないでください。"""

    response = await client.aio.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=AccusationJudgment,
        ),
    )

    try:
        result = json.loads(response.text)
        return AccusationJudgment(**result)
    except (json.JSONDecodeError, ValueError):
        logger.exception("Failed to parse accusation judgment")
        return AccusationJudgment(
            correct=False,
            explanation="判定中にエラーが発生しました。もう一度お試しください。",
        )

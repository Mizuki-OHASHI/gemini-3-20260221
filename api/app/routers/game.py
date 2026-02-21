from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException
from google.cloud.firestore_v1 import ArrayUnion

from app.firebase import db
from app.scenario import load_chapters
from app.schemas import (
    AnswerRequest,
    AnswerResponse,
    GameCreateRequest,
    GameResponse,
    GameUpdateRequest,
    HintUnlockRequest,
)

router = APIRouter(prefix="/game", tags=["game"])


@router.post("/", response_model=GameResponse)
async def create_game(req: GameCreateRequest):
    now = datetime.now(timezone.utc)
    doc_ref = db.collection("games").document()
    data = {
        "player_name": req.player_name,
        "status": "waiting",
        "current_chapter": 1,
        "current_phase": "explore",
        "unlocked_hints": [],
        "photo_count": 0,
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


@router.post("/{game_id}/unlock-hint", response_model=GameResponse)
async def unlock_hint(game_id: str, req: HintUnlockRequest):
    doc_ref = db.collection("games").document(game_id)
    doc = doc_ref.get()
    if not doc.exists:
        raise HTTPException(status_code=404, detail="Game not found")

    game_data = doc.to_dict()
    chapter_num = game_data.get("current_chapter", 1)
    chapters = load_chapters()
    chapter = chapters.get(chapter_num)

    if not chapter:
        raise HTTPException(status_code=400, detail="Chapter not found")

    if req.hint_index < 0 or req.hint_index >= len(chapter.hints):
        raise HTTPException(status_code=400, detail="Invalid hint index")

    if req.hint_index in game_data.get("unlocked_hints", []):
        raise HTTPException(status_code=400, detail="Hint already unlocked")

    now = datetime.now(timezone.utc)
    doc_ref.update(
        {
            "unlocked_hints": ArrayUnion([req.hint_index]),
            "updated_at": now,
        }
    )

    updated_doc = doc_ref.get()
    return GameResponse(id=updated_doc.id, **updated_doc.to_dict())


@router.post("/{game_id}/answer", response_model=AnswerResponse)
async def check_answer(game_id: str, req: AnswerRequest):
    doc_ref = db.collection("games").document(game_id)
    doc = doc_ref.get()
    if not doc.exists:
        raise HTTPException(status_code=404, detail="Game not found")

    game_data = doc.to_dict()
    chapter_num = game_data.get("current_chapter", 1)
    chapters = load_chapters()
    chapter = chapters.get(chapter_num)

    if not chapter:
        raise HTTPException(status_code=400, detail="Chapter not found")

    if req.answer_text.strip().lower() == chapter.answer_keyword.lower():
        next_chapter_num = chapter_num + 1
        next_chapter = chapters.get(next_chapter_num)
        now = datetime.now(timezone.utc)

        if next_chapter:
            doc_ref.update(
                {
                    "current_chapter": next_chapter_num,
                    "current_phase": "explore",
                    "unlocked_hints": [],
                    "status": "playing",
                    "updated_at": now,
                }
            )
            return AnswerResponse(
                correct=True,
                message=f"正解！次のチャプター「{next_chapter.title}」へ進みます。",
                next_chapter=next_chapter_num,
            )
        else:
            doc_ref.update(
                {
                    "status": "solved",
                    "updated_at": now,
                }
            )
            return AnswerResponse(
                correct=True,
                message="おめでとうございます！すべての謎を解き明かしました。",
                next_chapter=None,
            )
    else:
        return AnswerResponse(
            correct=False,
            message="不正解です。もう一度探してみましょう。",
            next_chapter=None,
        )

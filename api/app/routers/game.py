from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException

from app.firebase import db
from app.schemas import (
    GameCreateRequest,
    GameResponse,
    GameUpdateRequest,
)

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

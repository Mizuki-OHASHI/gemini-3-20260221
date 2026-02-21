from fastapi import APIRouter

from app.firebase import db
from app.schemas import GameCreateRequest, GameResponse

router = APIRouter(prefix="/game", tags=["game"])


@router.post("/", response_model=GameResponse)
async def create_game(req: GameCreateRequest):
    doc_ref = db.collection("games").document()
    data = {"player_name": req.player_name, "status": "waiting"}
    doc_ref.set(data)
    return GameResponse(id=doc_ref.id, **data)


@router.get("/{game_id}", response_model=GameResponse)
async def get_game(game_id: str):
    doc = db.collection("games").document(game_id).get()
    return GameResponse(id=doc.id, **doc.to_dict())

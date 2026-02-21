from fastapi import APIRouter, HTTPException

from app.scenario import load_hint_messages
from app.schemas import HintMessage

router = APIRouter(prefix="/scenario", tags=["scenario"])


@router.get("/hints", response_model=list[HintMessage])
async def list_hint_messages_endpoint():
    messages = load_hint_messages()
    return [HintMessage(item=k, message=v) for k, v in messages.items()]


@router.get("/hints/{item}", response_model=HintMessage)
async def get_hint_message(item: str):
    messages = load_hint_messages()
    msg = messages.get(item)
    if msg is None:
        raise HTTPException(status_code=404, detail="Hint message not found")
    return HintMessage(item=item, message=msg)

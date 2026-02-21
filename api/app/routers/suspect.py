import csv
from functools import lru_cache
from pathlib import Path

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.firebase import db
from app.gemini import client

router = APIRouter(prefix="/suspect", tags=["suspect"])

_DATA_PATH = Path(__file__).resolve().parent.parent.parent / "data" / "scenarios" / "suspects.csv"


class SuspectCheckRequest(BaseModel):
    suspect: str
    reason: str


class SuspectCheckResponse(BaseModel):
    correct: bool
    message: str


@lru_cache(maxsize=1)
def _load_suspects() -> dict[int, dict]:
    """suspects.csv を読み込んでチャプターごとの辞書を返す。"""
    suspects: dict[int, dict] = {}
    with open(_DATA_PATH, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            suspects[int(row["chapter"])] = {
                "correct_suspect": row["correct_suspect"],
                "scoring_criteria": row["scoring_criteria"],
            }
    return suspects


async def _evaluate_reason(reason: str, scoring_criteria: str) -> bool:
    """Geminiで理由が採点基準を満たすか判定する。"""
    prompt = (
        "あなたは謎解きゲームの採点者です。\n"
        "プレイヤーが提出した理由が、以下の採点基準を満たしているか判定してください。\n"
        "「はい」または「いいえ」のみで答えてください。\n\n"
        f"採点基準: {scoring_criteria}\n\n"
        f"プレイヤーの理由: {reason}"
    )
    response = await client.aio.models.generate_content(
        model="gemini-2.5-flash-lite",
        contents=prompt,
    )
    text = response.text.strip().lower()
    return "はい" in text or "yes" in text


@router.post("/{game_id}/check", response_model=SuspectCheckResponse)
async def check_suspect(game_id: str, req: SuspectCheckRequest):
    """
    プレイヤーが選んだ容疑者と理由を判定する。
    容疑者が正しく、かつ理由が採点基準を満たせば correct=True を返す。
    """
    doc = db.collection("games").document(game_id).get()
    if not doc.exists:
        raise HTTPException(status_code=404, detail="Game not found")

    chapter_num = doc.to_dict().get("current_chapter", 1)
    suspects = _load_suspects()
    suspect_data = suspects.get(chapter_num)

    if not suspect_data:
        raise HTTPException(status_code=400, detail="Suspect data not found for this chapter")

    correct_suspect = suspect_data["correct_suspect"]
    scoring_criteria = suspect_data["scoring_criteria"]

    # 容疑者チェック
    if req.suspect.strip() != correct_suspect:
        return SuspectCheckResponse(
            correct=False,
            message=f"容疑者が違います。もう一度考えてみましょう。",
        )

    # 理由チェック（Gemini）
    reason_passed = await _evaluate_reason(req.reason, scoring_criteria)
    if reason_passed:
        return SuspectCheckResponse(
            correct=True,
            message="正解！容疑者も理由も正しいです。",
        )
    else:
        return SuspectCheckResponse(
            correct=False,
            message="容疑者は合っていますが、理由が不十分です。もう少し具体的に考えてみましょう。",
        )

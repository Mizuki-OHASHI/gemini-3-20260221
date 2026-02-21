from datetime import datetime

from pydantic import BaseModel


# --- Game ---


class GameCreateRequest(BaseModel):
    player_name: str
    ghost_description: str = "長い黒髪の少女の幽霊。白いワンピースを着て、悲しげな表情をしている。"


class GameResponse(BaseModel):
    id: str
    player_name: str
    status: str
    photo_count: int
    ghost_description: str = ""
    avatar_url: str | None = None
    cleared_items: list[str] = []
    created_at: datetime
    updated_at: datetime


class AvatarResponse(BaseModel):
    game_id: str
    avatar_url: str


class GameUpdateRequest(BaseModel):
    status: str | None = None


# --- Photo ---


class PhotoResponse(BaseModel):
    id: str
    game_id: str
    original_url: str
    ghost_url: str | None = None
    ghost_gesture: str | None = None
    ghost_message: str | None = None
    detected_item: str | None = None
    created_at: datetime


class PhotoListResponse(BaseModel):
    photos: list[PhotoResponse]


# --- Scenario ---


class HintMessage(BaseModel):
    item: str
    message: str


# --- Turn ---


class VisionDetectionResult(BaseModel):
    detected_item: str | None = None
    confidence: str  # "high" | "medium" | "low" | "none"
    explanation: str


class TurnResponse(BaseModel):
    game_id: str
    photo_id: str
    original_url: str
    detected_item: str | None = None
    ghost_url: str | None = None
    ghost_message: str | None = None
    cleared_items: list[str]
    items_remaining: list[str]
    game_status: str  # "playing" | "solved"
    game_solved: bool
    hint_message: str
    message: str


# --- Accusation ---


class AccusationRequest(BaseModel):
    suspect_name: str
    reason: str


class AccusationJudgment(BaseModel):
    correct: bool
    explanation: str


class AccusationResponse(BaseModel):
    correct: bool
    message: str


# --- Gemini ---


class GenerateRequest(BaseModel):
    prompt: str
    model: str = "gemini-2.5-flash"


class GenerateResponse(BaseModel):
    text: str


class GenerateImageRequest(BaseModel):
    prompt: str


class GenerateImageResponse(BaseModel):
    image: str  # base64
    mime_type: str

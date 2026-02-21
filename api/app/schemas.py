from datetime import datetime

from pydantic import BaseModel


# --- Game ---


class GameCreateRequest(BaseModel):
    player_name: str


class GameResponse(BaseModel):
    id: str
    player_name: str
    status: str
    current_chapter: int
    current_phase: str
    unlocked_hints: list[int]
    photo_count: int
    created_at: datetime
    updated_at: datetime


class GameUpdateRequest(BaseModel):
    status: str | None = None
    current_chapter: int | None = None
    current_phase: str | None = None


class HintUnlockRequest(BaseModel):
    hint_index: int


class AnswerRequest(BaseModel):
    answer_text: str


class AnswerResponse(BaseModel):
    correct: bool
    message: str
    next_chapter: int | None = None


# --- Photo ---


class PhotoResponse(BaseModel):
    id: str
    game_id: str
    chapter: int
    original_url: str
    ghost_url: str | None = None
    ghost_gesture: str | None = None
    ghost_message: str | None = None
    created_at: datetime


class PhotoListResponse(BaseModel):
    photos: list[PhotoResponse]


# --- Scenario ---


class ScenarioChapter(BaseModel):
    chapter: int
    title: str
    story: str
    hints: list[str]
    answer_keyword: str
    ghost_prompt_template: str


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

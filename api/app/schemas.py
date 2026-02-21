from pydantic import BaseModel


# --- Game ---

class GameCreateRequest(BaseModel):
    player_name: str


class GameResponse(BaseModel):
    id: str
    player_name: str
    status: str

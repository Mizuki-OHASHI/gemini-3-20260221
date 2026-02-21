from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import game, gemini, live, photo, scenario, storage, turn

app = FastAPI(title="Game API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(game.router)
app.include_router(gemini.router)
app.include_router(live.router)
app.include_router(storage.router)
app.include_router(photo.router)
app.include_router(scenario.router)
app.include_router(turn.router)


@app.get("/health")
async def health():
    return {"status": "ok"}

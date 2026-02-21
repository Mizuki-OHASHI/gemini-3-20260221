from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import game, gemini, live, photo, scenario, storage

app = FastAPI(title="Game API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(game.router)
app.include_router(gemini.router)
app.include_router(live.router)
app.include_router(storage.router)
app.include_router(photo.router)
app.include_router(scenario.router)


@app.get("/health")
async def health():
    return {"status": "ok"}

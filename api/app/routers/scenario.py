from fastapi import APIRouter, HTTPException

from app.scenario import load_chapters
from app.schemas import ScenarioChapter

router = APIRouter(prefix="/scenario", tags=["scenario"])


@router.get("/chapters", response_model=list[ScenarioChapter])
async def list_chapters():
    chapters = load_chapters()
    return sorted(chapters.values(), key=lambda c: c.chapter)


@router.get("/chapters/{chapter}", response_model=ScenarioChapter)
async def get_chapter(chapter: int):
    chapters = load_chapters()
    ch = chapters.get(chapter)
    if not ch:
        raise HTTPException(status_code=404, detail="Chapter not found")
    return ch

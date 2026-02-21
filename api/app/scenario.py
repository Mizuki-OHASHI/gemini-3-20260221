import csv
import re
from functools import lru_cache
from pathlib import Path

from app.schemas import ScenarioChapter

DATA_DIR = Path(__file__).resolve().parent.parent / "data" / "scenarios"


def _parse_markdown(text: str) -> tuple[str, list[str]]:
    """Parse a chapter markdown file into story and hints."""
    # Remove frontmatter
    text = re.sub(r"^---.*?---\s*", "", text, flags=re.DOTALL)

    # Split on ## Hints
    parts = re.split(r"^## Hints\s*$", text, flags=re.MULTILINE)
    story = parts[0].strip()
    hints: list[str] = []
    if len(parts) > 1:
        for line in parts[1].strip().splitlines():
            m = re.match(r"^\d+\.\s+(.+)$", line.strip())
            if m:
                hints.append(m.group(1))
    return story, hints


@lru_cache(maxsize=1)
def load_chapters() -> dict[int, ScenarioChapter]:
    """Load all scenario chapters from CSV + Markdown files."""
    chapters: dict[int, ScenarioChapter] = {}

    with open(DATA_DIR / "chapters.csv", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            chapter_num = int(row["chapter"])
            md_path = DATA_DIR / f"chapter_{chapter_num:02d}.md"
            story, hints = _parse_markdown(md_path.read_text(encoding="utf-8"))

            chapters[chapter_num] = ScenarioChapter(
                chapter=chapter_num,
                title=row["title"],
                story=story,
                hints=hints,
                answer_keyword=row["answer_keyword"],
                ghost_prompt_template=row["ghost_prompt_template"],
            )

    return chapters

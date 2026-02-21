import base64

import httpx
from fastapi import APIRouter, HTTPException
from google.genai import types
from pydantic import BaseModel

from app.config import NANOBANANA_API_KEY, NANOBANANA_API_URL
from app.gemini import client

router = APIRouter(prefix="/image", tags=["image"])


class ImageGenRequest(BaseModel):
    prompt: str
    spec: str
    max_retries: int = 3


class ImageGenResponse(BaseModel):
    image_base64: str
    mime_type: str
    attempts: int
    passed: bool


async def _generate_image(prompt: str) -> tuple[bytes, str]:
    """Nanobanana APIで画像を生成して (bytes, mime_type) を返す。"""
    headers = {}
    if NANOBANANA_API_KEY:
        headers["Authorization"] = f"Bearer {NANOBANANA_API_KEY}"

    async with httpx.AsyncClient(timeout=60.0) as http:
        resp = await http.post(
            NANOBANANA_API_URL,
            headers=headers,
            json={"prompt": prompt},
        )
        resp.raise_for_status()

    content_type = resp.headers.get("content-type", "image/png").split(";")[0].strip()

    # レスポンスが JSON の場合（URL または base64 で返す API に対応）
    if "application/json" in content_type:
        data = resp.json()
        if "image" in data:
            image_bytes = base64.b64decode(data["image"])
            mime_type = data.get("mime_type", "image/png")
        elif "url" in data:
            async with httpx.AsyncClient(timeout=60.0) as http:
                img_resp = await http.get(data["url"])
                img_resp.raise_for_status()
            image_bytes = img_resp.content
            mime_type = img_resp.headers.get("content-type", "image/png").split(";")[0].strip()
        else:
            raise HTTPException(status_code=502, detail="Nanobanana API returned unexpected JSON structure")
    else:
        image_bytes = resp.content
        mime_type = content_type

    return image_bytes, mime_type


async def _check_spec(image_bytes: bytes, mime_type: str, spec: str) -> bool:
    """Geminiで画像が仕様を満たすか判定する。"""
    response = await client.aio.models.generate_content(
        model="gemini-2.0-flash",
        contents=[
            types.Part.from_bytes(data=image_bytes, mime_type=mime_type),
            (
                "以下の仕様を画像が満たしているか判定してください。"
                "「はい」または「いいえ」のみで答えてください。\n\n"
                f"仕様: {spec}"
            ),
        ],
    )
    text = response.text.strip().lower()
    return "はい" in text or "yes" in text


@router.post("/generate", response_model=ImageGenResponse)
async def generate_and_check(req: ImageGenRequest):
    """
    Nanobananaで画像を生成し、Geminiで仕様チェックを行う。
    仕様を満たせばそのまま返し、満たさなければmax_retriesまで再生成する。
    """
    last_image_bytes: bytes = b""
    last_mime_type: str = "image/png"

    for attempt in range(1, req.max_retries + 1):
        last_image_bytes, last_mime_type = await _generate_image(req.prompt)
        passed = await _check_spec(last_image_bytes, last_mime_type, req.spec)

        if passed:
            return ImageGenResponse(
                image_base64=base64.b64encode(last_image_bytes).decode(),
                mime_type=last_mime_type,
                attempts=attempt,
                passed=True,
            )

    # max_retries 回試しても仕様を満たさなかった場合は最後の画像を返す
    return ImageGenResponse(
        image_base64=base64.b64encode(last_image_bytes).decode(),
        mime_type=last_mime_type,
        attempts=req.max_retries,
        passed=False,
    )

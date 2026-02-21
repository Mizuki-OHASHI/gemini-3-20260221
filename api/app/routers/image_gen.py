import base64

from fastapi import APIRouter, HTTPException
from google.genai import types
from pydantic import BaseModel

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
    """Gemini SDK (gemini-2.0-flash-exp-image-generation) で画像を生成して (bytes, mime_type) を返す。"""
    response = await client.aio.models.generate_content(
        model="gemini-2.0-flash-exp-image-generation",
        contents=prompt,
        config=types.GenerateContentConfig(
            response_modalities=["IMAGE", "TEXT"],
        ),
    )

    for part in response.candidates[0].content.parts:
        if part.inline_data:
            return part.inline_data.data, part.inline_data.mime_type

    raise HTTPException(status_code=500, detail="Gemini did not return an image")


async def _check_spec(image_bytes: bytes, mime_type: str, spec: str) -> bool:
    """Geminiで画像が仕様を満たすか判定する。"""
    response = await client.aio.models.generate_content(
        model="gemini-2.5-flash-lite",
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
    Gemini (NanoBanana) で画像を生成し、仕様チェックを行う。
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

import base64

from fastapi import APIRouter
from google.genai import types

from app.gemini import client
from app.schemas import (
    GenerateImageRequest,
    GenerateImageResponse,
    GenerateRequest,
    GenerateResponse,
)

router = APIRouter(prefix="/gemini", tags=["gemini"])


@router.post("/generate", response_model=GenerateResponse)
async def generate(req: GenerateRequest):
    response = await client.aio.models.generate_content(
        model=req.model,
        contents=req.prompt,
    )
    return GenerateResponse(text=response.text)


@router.post("/generate-image", response_model=GenerateImageResponse)
async def generate_image(req: GenerateImageRequest):
    response = await client.aio.models.generate_content(
        model="nano-banana-pro-preview",
        contents=req.prompt,
        config=types.GenerateContentConfig(
            response_modalities=["IMAGE", "TEXT"],
        ),
    )
    for part in response.candidates[0].content.parts:
        if part.inline_data:
            return GenerateImageResponse(
                image=base64.b64encode(part.inline_data.data).decode(),
                mime_type=part.inline_data.mime_type,
            )
    return GenerateImageResponse(image="", mime_type="")

import asyncio
import json

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from google.genai import types

from app.gemini import client

router = APIRouter(tags=["live"])


@router.websocket("/ws/live")
async def live_session(ws: WebSocket):
    await ws.accept()

    config = types.LiveConnectConfig(
        response_modalities=["TEXT"],
    )

    async with client.aio.live.connect(
        model="gemini-2.0-flash-exp",
        config=config,
    ) as session:
        async def recv_from_gemini():
            try:
                while True:
                    async for response in session.receive():
                        if response.text:
                            await ws.send_json({"type": "text", "data": response.text})
            except asyncio.CancelledError:
                pass

        recv_task = asyncio.create_task(recv_from_gemini())

        try:
            while True:
                raw = await ws.receive_text()
                msg = json.loads(raw)
                await session.send(input=msg.get("text", ""), end_of_turn=True)
        except WebSocketDisconnect:
            recv_task.cancel()
            await recv_task

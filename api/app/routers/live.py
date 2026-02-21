import asyncio
import base64
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
        model="gemini-2.0-flash-live-001",
        config=config,
    ) as session:

        async def recv_from_gemini():
            try:
                while True:
                    async for response in session.receive():
                        if response.text:
                            await ws.send_json({"type": "text", "data": response.text})
                        if response.server_content and response.server_content.turn_complete:
                            await ws.send_json({"type": "turn_complete"})
            except asyncio.CancelledError:
                pass

        recv_task = asyncio.create_task(recv_from_gemini())

        try:
            while True:
                raw = await ws.receive_text()
                msg = json.loads(raw)
                msg_type = msg.get("type", "text")

                if msg_type == "text":
                    await session.send_client_content(
                        turns=msg.get("data", ""),
                        turn_complete=True,
                    )
                elif msg_type == "image":
                    data = base64.b64decode(msg["data"])
                    mime_type = msg.get("mime_type", "image/jpeg")
                    await session.send_realtime_input(
                        video=types.Blob(data=data, mime_type=mime_type),
                    )
                elif msg_type == "end_of_turn":
                    await session.send_client_content(turn_complete=True)

        except WebSocketDisconnect:
            recv_task.cancel()
            await recv_task

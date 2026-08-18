import asyncio
import json
import structlog
import redis.asyncio as redis
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from ..config import Settings

logger = structlog.get_logger(__name__)
router = APIRouter(prefix="/ws", tags=["WebSockets"])
settings = Settings()

active_connections: list[WebSocket] = []
redis_client = None
pubsub = None

async def redis_listener():
    global redis_client, pubsub
    try:
        redis_client = redis.from_url(settings.REDIS_URL)
        pubsub = redis_client.pubsub()
        await pubsub.subscribe("batman_events")
        logger.info("redis_pubsub_subscribed", channel="batman_events")
        
        async for message in pubsub.listen():
            if message["type"] == "message":
                payload = message["data"].decode("utf-8")
                # Forward to all websockets
                dead_connections = []
                for connection in active_connections:
                    try:
                        await connection.send_text(payload)
                    except Exception:
                        dead_connections.append(connection)
                for dead in dead_connections:
                    active_connections.remove(dead)
    except Exception as e:
        logger.error("redis_pubsub_error", error=str(e))

@router.on_event("startup")
async def startup_event():
    asyncio.create_task(redis_listener())

@router.on_event("shutdown")
async def shutdown_event():
    if pubsub:
        await pubsub.unsubscribe("batman_events")
    if redis_client:
        await redis_client.close()

@router.websocket("/alerts")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    active_connections.append(websocket)
    logger.info("websocket_connected", client=websocket.client)
    try:
        while True:
            data = await websocket.receive_text()
    except WebSocketDisconnect:
        if websocket in active_connections:
            active_connections.remove(websocket)
        logger.info("websocket_disconnected", client=websocket.client)


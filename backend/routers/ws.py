from fastapi import APIRouter, WebSocket, WebSocketDisconnect
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

@router.websocket("/live")
async def websocket_endpoint(websocket: WebSocket):
    from backend.main import ws_manager
    await ws_manager.connect(websocket)
    try:
        while True:
            # We don't really expect client to send us data for now, 
            # just keep the connection open
            data = await websocket.receive_text()
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        ws_manager.disconnect(websocket)

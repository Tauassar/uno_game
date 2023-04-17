import logging
from datetime import datetime
from typing import Union

from fastapi import WebSocket, WebSocketDisconnect
from . import router


logger = logging.getLogger(__name__)


class ConnectionManager:
    def __init__(self):
        self.connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.connections.append(websocket)

    async def broadcast(self, data: Union[dict, str]):
        for connection in self.connections:
            await connection.send_json(data)


manager = ConnectionManager()


@router.websocket(
    '/game/{game_session_id}',
)
async def websocket_endpoint(
    websocket: WebSocket,
    game_session_id: str,
):
    await manager.connect(websocket)

    while True:
        try:
            # Receive the JSON data sent by a client.
            data = await websocket.receive_json()
            # Some (fake) heavy data processing logic.
            message_processed = {
                **data,
                'processed': True,
                'game_session_id': game_session_id,
            }
            # Send JSON data to the client.
            await manager.broadcast(
                {
                    "message": message_processed,
                    "time": datetime.now().strftime("%H:%M:%S"),
                }
            )
        except WebSocketDisconnect:
            logger.info("The connection is closed.")
            break

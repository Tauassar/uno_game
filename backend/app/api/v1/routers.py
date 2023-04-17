import fastapi

from .endpoints import dummies
from .endpoints import token
from .endpoints import users
from .endpoints.game_sessions import websocket

api_router = fastapi.APIRouter()
api_router.include_router(dummies.router, tags=['dummies'])
api_router.include_router(token.router, tags=['token'])
api_router.include_router(users.router, tags=['users'])
api_router.include_router(websocket.router, tags=['websocket'])

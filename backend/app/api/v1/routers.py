import fastapi

from .endpoints import dummies
from .endpoints import token
from .endpoints import users


api_router = fastapi.APIRouter()
api_router.include_router(dummies.router, tags=['dummies'])
api_router.include_router(token.router, tags=['token'])
api_router.include_router(users.router, tags=['users'])

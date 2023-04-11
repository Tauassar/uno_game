import fastapi

from .endpoints import dummies
from .endpoints import token


api_router = fastapi.APIRouter()
api_router.include_router(dummies.router, tags=['dummies'])
api_router.include_router(token.router, tags=['token'])

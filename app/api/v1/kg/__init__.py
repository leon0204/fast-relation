from fastapi import APIRouter

from .kg import router

kg_router = APIRouter()
kg_router.include_router(router, tags=["kg模块"])

__all__ = ["kg_router"]

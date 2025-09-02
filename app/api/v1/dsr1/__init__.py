from fastapi import APIRouter

from .ds import router

ds_router = APIRouter()
ds_router.include_router(router, tags=["ds模块"])

__all__ = ["ds_router"]

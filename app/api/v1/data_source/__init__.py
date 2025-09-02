from fastapi import APIRouter

from .data_source import router

data_source_router = APIRouter()
data_source_router.include_router(router, tags=["数据源模块"])

__all__ = ["data_source_router"]

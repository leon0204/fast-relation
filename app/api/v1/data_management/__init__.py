from fastapi import APIRouter

from .data_management import router

data_management_router = APIRouter()
data_management_router.include_router(router, tags=["数据管理模块"])

__all__ = ["data_management_router"]

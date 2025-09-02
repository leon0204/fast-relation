from fastapi import APIRouter

from .knowledge_calculate import router

knowledge_calculate_router = APIRouter()
knowledge_calculate_router.include_router(router, tags=["知识图谱模块"])

__all__ = ["knowledge_calculate_router"]

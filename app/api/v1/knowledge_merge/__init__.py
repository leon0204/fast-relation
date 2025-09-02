from fastapi import APIRouter

from .knowledge_merge import router

knowledge_merge_router = APIRouter()
knowledge_merge_router.include_router(router, tags=["知识图谱模块"])

__all__ = ["knowledge_merge_router"]

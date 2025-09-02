from fastapi import APIRouter

from .knowledge_graph import router

knowledge_graph_router = APIRouter()
knowledge_graph_router.include_router(router, tags=["知识图谱模块"])

__all__ = ["knowledge_graph_router"]

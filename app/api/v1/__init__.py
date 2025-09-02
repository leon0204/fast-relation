from fastapi import APIRouter

from app.core.dependency import DependPermission

from .apis import apis_router
from .auditlog import auditlog_router
from .base import base_router
from .depts import depts_router
from .menus import menus_router
from .roles import roles_router
from .users import users_router
from .kg import kg_router
from .data_source import data_source_router
from .knowledge_graph import knowledge_graph_router
from .knowledge_merge import knowledge_merge_router
from .knowledge_calculate import knowledge_calculate_router
from .data_management import data_management_router

v1_router = APIRouter()

v1_router.include_router(base_router, prefix="/base")
v1_router.include_router(users_router, prefix="/user", dependencies=[DependPermission])
v1_router.include_router(roles_router, prefix="/role", dependencies=[DependPermission])
v1_router.include_router(menus_router, prefix="/menu", dependencies=[DependPermission])
v1_router.include_router(apis_router, prefix="/api", dependencies=[DependPermission])
v1_router.include_router(depts_router, prefix="/dept", dependencies=[DependPermission])
v1_router.include_router(auditlog_router, prefix="/auditlog", dependencies=[DependPermission])
v1_router.include_router(kg_router, prefix="/kg", dependencies=[DependPermission])
v1_router.include_router(data_source_router, prefix="/datasource", dependencies=[DependPermission])
v1_router.include_router(data_management_router, prefix="/data_management", dependencies=[DependPermission])
v1_router.include_router(knowledge_graph_router, prefix="/knowledge_graph", dependencies=[DependPermission])
v1_router.include_router(knowledge_merge_router, prefix="/knowledge_merge")
v1_router.include_router(knowledge_calculate_router, prefix="/knowledge_calculate", dependencies=[DependPermission])


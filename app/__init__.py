from contextlib import asynccontextmanager

from fastapi import FastAPI
from tortoise import Tortoise

from app.core.exceptions import SettingNotFound
from app.core.init_app import (
    init_data,
    make_middlewares,
    register_exceptions,
    register_routers,
)
from loguru import logger

try:
    from app.settings.config import settings
except ImportError:
    raise SettingNotFound("Can not import settings")


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_data()
    yield
    await Tortoise.close_connections()


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.APP_TITLE,
        description=settings.APP_DESCRIPTION,
        version=settings.VERSION,
        openapi_url="/openapi.json",
        middleware=make_middlewares(),
        lifespan=lifespan,
    )
    register_exceptions(app)
    register_routers(app, prefix="/api")
    return app


    # @app.on_event("startup")
    # async def startup():
    #     """应用启动事件"""
    #     try:
    #         logger.info("正在启动知识图谱系统...")
    #         await db.connect()
    #         logger.success("知识图谱系统启动完成")
    #     except Exception as e:
    #         logger.error(f"启动失败: {str(e)}")
    #         raise
    #
    # @app.on_event("shutdown")
    # async def shutdown():
    #     """应用关闭事件"""
    #     try:
    #         logger.info("正在关闭知识图谱系统...")
    #         await db.close()
    #         logger.success("知识图谱系统已关闭")
    #     except Exception as e:
    #         logger.error(f"关闭过程中出错: {str(e)}")
    #
    # # 健康检查端点
    # @app.get("/health")
    # async def health_check():
    #     """健康检查"""
    #     return {"status": "healthy"}

app = create_app()

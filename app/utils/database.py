# from asyncpg import create_pool
# from asyncpg_dm import create_dm_pool
# import dmPython
from urllib.parse import quote

from elasticsearch import AsyncElasticsearch
from neo4j import AsyncGraphDatabase, GraphDatabase

from typing import AsyncGenerator
from app.settings import settings
import logging

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

logger = logging.getLogger(__name__)


class Database:
    def __init__(self):
        self.dm_pool = None
        self.es_client = None
        self.neo4j_driver = None
        self.dm_sync_conn = None

        self.dm_engine = None
        self.dm_session = None
        self.dm_url = None

    async def connect_dm(self):
        # 达梦 SQLAlchemy 驱动
        settings.DM_PASSWORD = quote(settings.DM_PASSWORD)
        self.dm_url = f"dm://{settings.DM_USER}:{settings.DM_PASSWORD}@{settings.DM_HOST}:{settings.DM_PORT}"
        connect_args = {
            'schema': settings.DM_DATABASE,
            'connection_timeout': 15
        }

        self.dm_engine = create_engine(self.dm_url, connect_args=connect_args, echo=True, pool_size=10,
                                       pool_timeout=30, pool_recycle=3600, pool_pre_ping=True)
        self.dm_session = sessionmaker(bind=self.dm_engine, autoflush=False, autocommit=False, expire_on_commit=False)
        logger.info("达梦数据库 SQLAlchemy 引擎创建成功")

    async def close_dm(self):
        self.dm_engine.dispose()
        logger.info("达梦数据库 SQLAlchemy 引擎已关闭")

    async def connect_es(self):
        # Elasticsearch异步客户端
        self.es_client = AsyncElasticsearch(
            f"http://{settings.ES_HOSTS}",
            basic_auth=(settings.ES_USER, settings.ES_PASSWORD) if settings.ES_USER else None,
            request_timeout=60,
        )
        logger.info("Elasticsearch客户端创建成功")

    async def close_es(self):
        self.es_client.close()
        logger.info("Elasticsearch客户端已关闭")

    def connect_to_neo4j(self):
        try:
            self.neo4j_driver = GraphDatabase.driver(settings.NEO4J_URI,
                                                     auth=(settings.NEO4J_USER, settings.NEO4J_PASSWORD))
            logger.info("成功连接到Neo4j数据库")
        except Exception as e:
            logger.error(f"连接Neo4j数据库失败: {str(e)}")
            self.neo4j_driver = None

    def close_neo4j(self):
        try:
            if self.neo4j_driver:
                self.neo4j_driver.close()
            logger.info("数据库连接已关闭")
        except Exception as e:
            logger.error(f"关闭数据库连接时出错: {str(e)}")

    async def connect(self):
        """初始化所有数据库连接"""
        try:
            # Neo4j异步驱动
            self.neo4j_driver = AsyncGraphDatabase.driver(
                settings.NEO4J_URI,
                auth=(settings.NEO4J_USER, settings.NEO4J_PASSWORD)
            )
            logger.info("Neo4j驱动创建成功")

        except Exception as e:
            logger.error(f"数据库连接失败: {str(e)}")
            raise

    async def close(self):
        """关闭所有数据库连接"""
        try:
            if self.dm_pool:
                await self.dm_pool.close()
            if self.dm_sync_conn:
                self.dm_sync_conn.close()
            if self.es_client:
                await self.es_client.close()
            if self.neo4j_driver:
                await self.neo4j_driver.close()
            logger.info("数据库连接已关闭")
        except Exception as e:
            logger.error(f"关闭数据库连接时出错: {str(e)}")


# 全局数据库实例
db = Database()


# 依赖注入
async def get_dm_db() -> AsyncGenerator:
    """获取达梦数据库异步连接"""
    async with db.dm_pool.acquire() as conn:
        try:
            yield conn
        except Exception as e:
            logger.error(f"获取达梦数据库连接出错: {str(e)}")
            raise


async def get_neo4j_db():
    if db.neo4j_driver is None:
        await db.connect()
    async with db.neo4j_driver.session() as session:
        yield session


def get_neo4j_db_sync():
    if db.neo4j_driver is None:
        db.connect_to_neo4j()
        return db.neo4j_driver
    else:
        return db.neo4j_driver


async def get_db_session() -> AsyncGenerator:
    """获取 SQLAlchemy Session"""
    if not hasattr(db, 'dm_engine') or db.dm_engine is None:
        await db.connect_dm()

    db_session = db.dm_session()
    try:
        logger.debug("数据库会话创建成功")
        yield db_session
    except Exception as e:
        db_session.rollback()
        logger.error(f"数据库操作失败: {str(e)}")
        raise
    finally:
        db_session.close()  # 确保 session 被正确关闭


async def get_es_session():
    if not hasattr(db, 'es_client') or db.es_client is None:
        await db.connect_es()

    yield db.es_client


SQLAlchemyBase = declarative_base()

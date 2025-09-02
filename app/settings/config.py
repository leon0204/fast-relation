import os
import typing
from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict

env = os.getenv("ENV", "prod")
env_file_path = f".env.{env}"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=env_file_path, env_file_encoding="utf-8")

    VERSION: str = "0.1.0"
    APP_TITLE: str = "Vue FastAPI Admin"
    PROJECT_NAME: str = "Vue FastAPI Admin"
    APP_DESCRIPTION: str = "Description"

    CORS_ORIGINS: typing.List = ["*"]
    CORS_ALLOW_CREDENTIALS: bool = True
    CORS_ALLOW_METHODS: typing.List = ["*"]
    CORS_ALLOW_HEADERS: typing.List = ["*"]

    DEBUG: bool = True

    PROJECT_ROOT: str = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
    BASE_DIR: str = os.path.abspath(os.path.join(PROJECT_ROOT, os.pardir))
    LOGS_ROOT: str = os.path.join(BASE_DIR, "app/logs")
    SECRET_KEY: str = "3488a63e1765035d386f05409663f55c83bfae3b3c61a932744b20ad14244dcf"  # openssl rand -hex 32
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 day
    TORTOISE_ORM: dict = {
        "connections": {
            # SQLite configuration
            "sqlite": {
                "engine": "tortoise.backends.sqlite",
                "credentials": {"file_path": f"{BASE_DIR}/db.sqlite3"},  # Path to SQLite database file
            },
            # MySQL/MariaDB configuration
            # Install with: tortoise-orm[asyncmy]
            # "mysql": {
            #     "engine": "tortoise.backends.mysql",
            #     "credentials": {
            #         "host": "localhost",  # Database host address
            #         "port": 3306,  # Database port
            #         "user": "yourusername",  # Database username
            #         "password": "yourpassword",  # Database password
            #         "database": "yourdatabase",  # Database name
            #     },
            # },
            # PostgreSQL configuration
            # Install with: tortoise-orm[asyncpg]
            # "postgres": {
            #     "engine": "tortoise.backends.asyncpg",
            #     "credentials": {
            #         "host": "localhost",  # Database host address
            #         "port": 5432,  # Database port
            #         "user": "yourusername",  # Database username
            #         "password": "yourpassword",  # Database password
            #         "database": "yourdatabase",  # Database name
            #     },
            # },
            # MSSQL/Oracle configuration
            # Install with: tortoise-orm[asyncodbc]
            # "oracle": {
            #     "engine": "tortoise.backends.asyncodbc",
            #     "credentials": {
            #         "host": "localhost",  # Database host address
            #         "port": 1433,  # Database port
            #         "user": "yourusername",  # Database username
            #         "password": "yourpassword",  # Database password
            #         "database": "yourdatabase",  # Database name
            #     },
            # },
            # SQLServer configuration
            # Install with: tortoise-orm[asyncodbc]
            # "sqlserver": {
            #     "engine": "tortoise.backends.asyncodbc",
            #     "credentials": {
            #         "host": "localhost",  # Database host address
            #         "port": 1433,  # Database port
            #         "user": "yourusername",  # Database username
            #         "password": "yourpassword",  # Database password
            #         "database": "yourdatabase",  # Database name
            #     },
            # },
        },
        "apps": {
            "models": {
                "models": ["app.models", "aerich.models"],
                "default_connection": "sqlite",
            },
        },
        "use_tz": False,  # Whether to use timezone-aware datetimes
        "timezone": "Asia/Shanghai",  # Timezone setting
    }
    DATETIME_FORMAT: str = "%Y-%m-%d %H:%M:%S"

    # Elasticsearch配置
    ES_HOSTS: str = "localhost:9200"
    ES_INDEX: str = ""
    ES_USER: Optional[str] = None
    ES_PASSWORD: Optional[str] = None

    # Neo4j配置
    NEO4J_URI: str = "bolt://localhost:7687"
    NEO4J_USER: str = "neo4j"
    NEO4J_PASSWORD: str = "neo4j123"

    # 达梦配置
    DM_HOST: str = "localhost"
    DM_PORT: int = 5236
    DM_USER: str = "SYSDBA"
    DM_PASSWORD: str = "SYSDBA123"
    DM_DATABASE: str = "TEST"

    # NLP配置
    NLP_MODEL: str = "zh_core_web_md"
    SIMILARITY_THRESHOLD: float = 0.85

    custom_names: list = ['侯亮平', '李达康', '祁同伟', '陈岩石', '陆亦可', '高育良', '沙瑞金', '高小琴', '高小凤', '赵东来', '程度', '吴惠芬', '赵瑞龙',
                          '赵立春', '陈海', '梁璐', '刘新建', '欧阳菁', '吴心怡', '蔡成功', '丁义珍', "周恩来", "邓颖超", "段延庆", "黄眉僧", "段誉",
                          "侯宝林", "郭启儒", "刘宝瑞", "郭全宝", "张三", "李四", "曹雪芹", "刘德华", "梁朝伟", "张嘉译", "赵六", "李雷", "韩梅梅"]


settings = Settings()

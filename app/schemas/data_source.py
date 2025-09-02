from pydantic import BaseModel, Field
from typing import Optional, List, Dict
from datetime import datetime
from enum import Enum


class DataSourceStatus(Enum):
    ENABLED = 1  # 启用
    DISABLED = 0  # 禁用
    ALL = -1  # 所有状态（仅用于查询）


class DataSourceCreateRequest(BaseModel):
    name: str = Field(..., description="数据源名称")
    description: Optional[str] = Field(None, description="描述")
    data_type: str = Field(..., description="数据分类：结构化/非结构化/半结构化")
    db_type: str = Field(..., description="数据库类型：hbase/flink/es")
    ip_address: Optional[str] = Field(None, description="地址")
    port: Optional[int] = Field(None, description="端口号")
    username: Optional[str] = Field(None, description="用户名")
    password: Optional[str] = Field(None, description="密码")
    schema_table: Optional[str] = Field(None, description="库")
    table_name: Optional[str] = Field(None, description="表名")
    enabled: bool = Field(default=True, description="当前状态")
    created_by: Optional[str] = Field(None, description="创建人")


class DataSourceUpdateRequest(BaseModel):
    name: Optional[str] = Field(None, description="数据源名称")
    description: Optional[str] = Field(None, description="描述")
    data_type: Optional[str] = Field(None, description="数据分类：结构化/非结构化/半结构化")
    db_type: Optional[str] = Field(None, description="数据库类型：hbase/flink/es")
    ip_address: Optional[str] = Field(None, description="地址")
    port: Optional[int] = Field(None, description="端口号")
    username: Optional[str] = Field(None, description="用户名")
    password: Optional[str] = Field(None, description="密码")
    schema_table: Optional[str] = Field(None, description="库")
    table_name: Optional[str] = Field(None, description="表名")
    enabled: Optional[bool] = Field(None, description="当前状态")


class DataSource(BaseModel):
    id: Optional[int]
    source_id: Optional[str]
    name: str
    description: Optional[str]
    data_type: str
    db_type: str
    ip_address: Optional[str]
    port: Optional[int]
    username: Optional[str]
    password: Optional[str]
    schema_table: Optional[str]
    table_name: Optional[str]
    enabled: bool
    created_by: Optional[str]
    created_at: Optional[str]
    # updated_at: datetime


class DataSourceListData(BaseModel):
    total: int
    data: List[DataSource]


class DataSourceResponse(BaseModel):
    msg: str
    data: DataSource


class DataSourceListResponse(BaseModel):
    msg: str
    data: DataSourceListData


class DataSourceDeleteResponse(BaseModel):
    msg: str


class DataSourceBatchDeleteRequest(BaseModel):
    ids: List[int] = Field(None, description="要删除的数据源ID列表")


class DbType(str, Enum):
    HBASE = "HBase"
    FLINK = "Flink"
    ES = "Elasticsearch"
    DM = "Dameng"
    KAFKA = "Kafka"
    NEO4J = "Neo4j"


class ConnectionTestRequest(BaseModel):
    db_type: str = Field(..., description="数据库类型：hbase/flink/es")
    ip_address: Optional[str] = Field(None, description="地址")
    port: Optional[int] = Field(None, description="端口号")
    username: Optional[str] = Field(None, description="用户名")
    password: Optional[str] = Field(None, description="密码")
    schema_table: Optional[str] = Field(None, description="库")
    table_name: Optional[str] = Field(None, description="表名")


class TestResult(BaseModel):
    status: str
    message: str

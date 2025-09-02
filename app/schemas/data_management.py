from pydantic import BaseModel, Field
from typing import List, Optional, AnyStr, Any


# 数据源信息
class DataSourceModel(BaseModel):
    source_id: str = Field(..., description="数据源ID")
    name: str = Field(..., description="数据源名称")
    data_type: str = Field(..., description="数据分类：结构化/非结构化/半结构化")
    db_type: str = Field(..., description="数据库类型：hbase/flink/es")
    schema_table: str = Field(..., description="库")
    table_name: str = Field(..., description="表名")


class DataSourceRequest(BaseModel):
    source_id: str = Field(..., description="数据源ID")
    name: str = Field(..., description="数据源名称")
    data_type: str = Field(..., description="数据分类：结构化/非结构化/半结构化")
    db_type: str = Field(..., description="数据库类型：hbase/flink/es")
    ip_address: str = Field(..., description="地址")
    port: int = Field(..., description="端口号")
    username: Optional[str] = Field(None, description="用户名")
    password: Optional[str] = Field(None, description="密码")
    schema_table: str = Field(..., description="库")
    table_name: str = Field(..., description="表名")
    fields: Optional[List[str]] = Field(None, description="达梦的字段")
    kafka_msg_limit: Optional[int] = Field(None, description="kafka的数据量限制")


class DataManagementItem(BaseModel):
    id: str
    data_source: DataSourceModel = Field(..., description="数据源信息")
    data: Any = Field(..., description="数据")
    synced_at: str = Field(..., description="同步时间")


class DataManagementListResponse(BaseModel):
    total: int
    data: List[DataManagementItem]


class DataManagementResponse(BaseModel):
    msg: str


class DataSourceBulkDeleteRequest(BaseModel):
    ids: dict[str, List[str]]


class DamengFieldsResponse(BaseModel):
    fields: List[str]

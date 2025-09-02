from pydantic import BaseModel, field_validator
from typing import Dict, Optional, Any, List
from datetime import datetime
from enum import Enum


# 模型类型枚举定义
class ModelType(str, Enum):
    """知识图谱模型类型枚举"""
    KNOWLEDGE_GRAPH = "knowledge_graph"  # 知识图谱模型
    ENTITY = "entity"
    RELATION = "relation"
    # SEMANTIC_NETWORK = "semantic_network"  # 语义网络模型
    # ONTOLOGY = "ontology"  # 本体模型


class DefaultName(str, Enum):
    DEFAULT_ENTITY_NAME = "NEW_ENTITY"
    DEFAULT_RELATION_TYPE = "NEW_RELATION"


# 知识图谱模型
class KnowledgeGraphModel(BaseModel):
    """知识图谱模型定义"""
    id: Optional[str] = None  # 模型唯一标识符
    name: str  # 模型名称
    created_by: str = ""  # 创建人
    description: Optional[str] = None  # 模型描述
    type: ModelType = ModelType.KNOWLEDGE_GRAPH  # 模型类型
    # status: ModelStatus = ModelStatus.INACTIVE  # 模型状态
    created_at: str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")  # 创建时间
    updated_at: str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")  # 更新时间
    # config: ModelConfig = ModelConfig()  # 模型配置
    # statistics: Dict[str, Any] = {}  # 模型统计信息


class KnowledgeGraphUpdateRequest(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None


class KnowledgeGraphModelListData(BaseModel):
    total: int
    data: List[KnowledgeGraphModel] = []


class KnowledgeGraphModelList(BaseModel):
    msg: str
    data: KnowledgeGraphModelListData = {"total": 0, "data": []}


# 实体数据模型
class EntityModel(BaseModel):
    """知识图谱实体模型"""
    id: Optional[str] = None  # 实体唯一标识符
    name: str  # 实体名称
    type: ModelType = ModelType.ENTITY  # 实体类型
    email: Optional[str] = None  # 邮箱
    properties: Dict[str, Any] = {}  # 实体属性字典
    model_id: Optional[str] = None  # 所属模型ID


class EntityModelListData(BaseModel):
    total: int
    data: List[EntityModel] = []


class EntityModelList(BaseModel):
    msg: str
    data: EntityModelListData = {"total": 0, "data": []}


class EntityCreateBulkRequest(BaseModel):
    data: List[EntityModel]


class EntityUpdateRequest(BaseModel):
    name: Optional[str] = None
    type: Optional[str] = None
    properties: Optional[Dict[str, Any]] = None


# 关系数据模型
class RelationModel(BaseModel):
    """知识图谱关系模型"""
    id: Optional[str] = None  # 关系唯一标识符
    source_id: str  # 源实体ID
    target_id: str  # 目标实体ID
    type: str  # 关系类型
    properties: Dict[str, Any] = {}  # 关系属性字典
    model_id: Optional[str] = None  # 所属模型ID


class RelationUpdateRequest(BaseModel):
    type: Optional[str] = None
    properties: Optional[Dict[str, Any]] = None


# 默认实体和默认关系
class CreateEntityAndRelationRequest(BaseModel):
    id: str
    model_id: Optional[str] = None


class CreateEntityAndRelationResponse(BaseModel):
    entity: EntityModel
    relation: RelationModel


class RelationCreateBulkRequest(BaseModel):
    data: List[RelationModel]

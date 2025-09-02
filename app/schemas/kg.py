from pydantic import BaseModel


class EntityRequest(BaseModel):
    sentence: str


class EntityItem(BaseModel):
    text: str
    label: str


class EntityResponse(BaseModel):
    entities: list[EntityItem]  # 包含实体列表


class Relation(BaseModel):
    text: str


class RelationRequest(BaseModel):
    sentence: str
    entity1: str
    entity2: str


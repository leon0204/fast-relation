from pydantic import BaseModel, field_validator
from typing import Dict, Optional, Any, List


class EntityRepairRequest(BaseModel):
    entity_list: List[str]
    entity_id: str


class QueryRequest(BaseModel):
    question: str


class LinkRequest(BaseModel):
    sentence: str
    model_id: str


class QueryResult(BaseModel):
    type: str  # "name", "relation_path", "property"
    result: List[Dict[str, Any]]
    timestamp: str

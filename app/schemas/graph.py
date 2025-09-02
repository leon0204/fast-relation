from pydantic import BaseModel
from typing import List


class RelationCreate(BaseModel):
    head: str
    tail: str
    relation_type: str
    text: str


class BulkRelationCreate(BaseModel):
    relations: List[RelationCreate]

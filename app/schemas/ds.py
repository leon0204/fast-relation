from pydantic import BaseModel


# 上传知识库的数据模型
class KnowledgeItem(BaseModel):
    id: int
    question: str
    answer: str


# 查询知识库的数据模型
class QueryItem(BaseModel):
    question: str


class RelationItem(BaseModel):
    h: dict  # 包含 name 和 pos
    t: dict  # 包含 name 和 pos
    relation: str
    text: str

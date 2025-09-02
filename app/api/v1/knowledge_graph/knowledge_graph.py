import logging
from datetime import datetime
from typing import Optional, List

from fastapi import APIRouter, Query, Body, Path, Depends
from fastapi.exceptions import HTTPException

from app.core.dependency import AuthControl

from app.controllers.knowledge_graph import knowledgeGraphController as kgController
from app.models import User
from app.schemas.knowledge_graph import (
    KnowledgeGraphModel, KnowledgeGraphUpdateRequest, KnowledgeGraphModelList, EntityUpdateRequest, EntityModel,
    RelationModel, RelationUpdateRequest, EntityModelList, EntityCreateBulkRequest, CreateEntityAndRelationRequest,
    CreateEntityAndRelationResponse, RelationCreateBulkRequest
)

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/", summary="知识图谱API")
def read_root():
    return {"Hello": "欢迎使用知识图谱API"}


# 模型相关
@router.post("/model", summary="创建知识图谱模型")
def create_model(model: KnowledgeGraphModel, current_user: User = Depends(AuthControl.is_authed)):
    """创建知识图谱模型"""
    created_by = current_user.username if current_user else ""
    model.created_by = created_by
    return kgController.create_model(model)


@router.get("/model/list", summary="获取所有知识图谱模型")
def get_all_models(
        page: int = Query(1, description="页码"),
        page_size: int = Query(10, description="每页数量"),
):
    """获取所有知识图谱模型"""
    return KnowledgeGraphModelList(msg="success", data=kgController.get_models(page, page_size))


@router.get("/model/search", summary="搜索知识图谱模型")
def search_models(
        query: str = Query(..., description="搜索查询"),
        start_time: str = Query(None, description="开始时间 (ISO格式, 如: 2025-07-01T00:00:00)"),
        end_time: str = Query(None, description="结束时间 (ISO格式, 如: 2025-07-04T23:59:59)"),
        page: int = Query(1, description="页码"),
        page_size: int = Query(10, description="每页数量"),
):
    """搜索知识图谱模型"""
    try:
        if start_time is None:
            start_time = "1970-01-01T00:00:00"
        if end_time is None:
            end_time = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
        start = datetime.fromisoformat(start_time)
        end = datetime.fromisoformat(end_time)
        return KnowledgeGraphModelList(msg="success",
                                       data=kgController.search_model(query, (start, end), page, page_size))
    except ValueError as e:
        raise HTTPException(status_code=400, detail="时间格式不正确，例如: 2025-07-01 00:00:00")


@router.get("/model/{model_id}", summary="获取特定知识图谱模型")
def get_model(model_id: str):
    """获取特定知识图谱模型"""
    return kgController.get_model(model_id)


@router.put("/model/{model_id}", summary="更新知识图谱模型")
def update_model(model_id: str, updated_model: KnowledgeGraphUpdateRequest):
    """更新知识图谱模型"""
    return kgController.update_model(model_id, updated_model)


@router.delete("/model/{model_id}", summary="删除知识图谱模型")
def delete_model(model_id: str):
    """删除知识图谱模型"""
    return kgController.delete_model(model_id)


@router.get("/kg/entity/list", summary="获取模型下所有实体")
def get_entity_list(
        model_id: str = Query(..., description="模型ID"),
        page: int = Query(1, description="页码"),
        page_size: int = Query(500, description="每页数量"),
):
    """获取指定知识图谱模型下的所有实体列表。"""
    try:
        entities = kgController.get_entities_by_model(model_id, page, page_size)
        return EntityModelList(msg="success", data=entities)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取实体列表失败：{e}")


@router.get("/kg/entity/search", summary="搜索实体")
def search_entities(
        query: str = Query(..., description="搜索关键词"),
        model_id: str = Query(..., description="可选：按模型ID筛选"),
        entity_type: Optional[str] = Query(None, description="可选：按实体类型筛选"),
        limit: int = Query(200, ge=1, description="结果数量限制")
):
    try:
        entities = kgController.search_entities(query, model_id, entity_type, limit)
        return entities
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"搜索失败：{e}")


@router.post("/kg/entity", summary="创建实体")
def create_entity(
        model_id: str = Query(..., description="模型ID"),
        entity: EntityModel = Body(..., description="实体信息")
):
    """创建实体"""
    return kgController.create_entity(model_id, entity)


@router.post("/kg/entity-relation", summary="创建新实体并关联新关系")
def create_default_entity_and_relation(
        model_id: str = Query(..., description="模型ID"),
        entity: CreateEntityAndRelationRequest = Body(..., description="实体ID"),
):
    try:
        new_entity, new_relation = kgController.create_entity_and_relation(model_id, entity.id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return CreateEntityAndRelationResponse(entity=new_entity, relation=new_relation)


@router.post("/kg/entity/bulk", summary="批量创建实体")
def create_bulk_entities(
        model_id: str = Query(..., description="模型ID"),
        entities: EntityCreateBulkRequest = Body(..., description="实体信息列表")
):
    data = entities.data
    return kgController.create_bulk_entities(model_id, data)


@router.get("/kg/entity/{entity_id}", summary="查询单个实体")
def get_entity(
        entity_id: str = Path(..., description="实体ID")
):
    return kgController.get_entity(entity_id)


@router.put("/kg/entity/{entity_id}", summary="更新实体")
def update_entity(
        # model_id: str = Query(..., description="模型ID"),
        entity_id: str = Path(..., description="实体ID"),
        entity_update: EntityUpdateRequest = Body(..., description="要更新的实体信息")
):
    try:
        update_data = entity_update.model_dump(exclude_unset=True)
        updated_entity = kgController.update_entity(entity_id, update_data)
        return updated_entity
    except ValueError as e:
        raise HTTPException(status_code=404, detail=f"更新失败：{e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"更新失败：{e}")


@router.delete("/kg/entity/{entity_id}", summary="删除实体")
def delete_entity(
        # model_id: str = Query(..., description="模型ID"),
        entity_id: str = Path(..., description="要删除的实体ID")
):
    try:
        result = kgController.delete_entity(entity_id)
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=f"删除失败：{e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"删除失败：{e}")


@router.post("/kg/relation", summary="创建关系")
def create_relation(relation: RelationModel):
    """在两个实体之间创建关系"""
    try:
        new_relation = kgController.create_relation(relation)
        return new_relation
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"创建关系失败：{e}")


@router.post("/kg/relation/bulk", summary="批量创建关系")
def create_bulk_relations(data: RelationCreateBulkRequest):
    relations = data.data
    return kgController.create_bulk_relations(relations)


@router.get("/kg/relation/list", summary="获取所有关系")
def get_all_relations(model_id: str = Query(..., description="模型ID")):
    """获取数据库中所有关系的列表"""
    try:
        relations = kgController.get_all_relations(model_id)
        return relations
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取关系列表失败：{e}")


@router.get("/kg/relation/{relation_id}", summary="获取指定关系")
def get_relation(relation_id: str):
    """根据 ID 获取关系"""
    try:
        relation = kgController.get_relation(relation_id)
        return relation
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取关系失败：{e}")


@router.put("/kg/relation/{relation_id}", summary="更新关系")
def update_relation(
        relation_id: str = Path(..., description="关系ID"),
        relation_update: RelationUpdateRequest = Body(..., description="要更新的关系信息")
):
    """更新关系的属性"""
    try:
        update_data = relation_update.model_dump(exclude_unset=True)
        updated_relation = kgController.update_relation(relation_id, update_data)
        return updated_relation
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"更新关系失败：{e}")


@router.delete("/kg/relation/{relation_id}", summary="删除关系")
def delete_relation(relation_id: str):
    """根据 ID 删除关系"""
    try:
        result = kgController.delete_relation(relation_id)
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"删除关系失败：{e}")


@router.post("/algorithm", summary="获取算法")
def get_graph_algorithm(
        model_id: str = Query(..., description="模型ID"),
        algorithm: str = Query(..., description="算法ID"),
        start_entity_id: Optional[str] = Query(None, description="实体ID"),
        end_entity_id: Optional[str] = Query(None, description="实体ID"),
):
    if algorithm == "pagerank":
        return kgController.graph_algorithm_pagerank(model_id)
    elif algorithm == "community_detection":
        return kgController.graph_algorithm_community_detection_louvain(model_id)
    elif algorithm == "shortest_paths":
        return kgController.graph_algorithm_shortest_path(model_id, start_entity_id, end_entity_id)
    return {"message": "算法不存在"}


@router.post("/kg/default-entity-relation", summary="创建新实体并关联新关系")
def create_default_entities_and_relations(model_id: str = Query(..., description="模型ID")):
    return kgController.create_default_entities_and_relations(model_id)

import json

from app.schemas.base import Fail, Success
import logging

from fastapi import APIRouter, Query, Body, Path, Depends

from app.controllers.knowledge_calculate import KnowledgeCalculateController, GraphMiningAlgorithms
from app.controllers.knowledge_graph import knowledgeGraphController as kgController

from app.schemas.knowledge_graph import (
    RelationModel, EntityModelList, EntityModel
)

logger = logging.getLogger(__name__)

router = APIRouter()


# 知识推理算法
@router.post("/infer_transitive")
async def infer_transitive(
        model_id: str = Body(..., description="模型ID"),
        page: int = Body(1, description="页码"),
        page_size: int = Body(100, description="每页数量")
):
    try:
        entities = kgController.get_entities_by_model(model_id, page, page_size)
        relations = kgController.get_all_relations(model_id)

        reasoner = KnowledgeCalculateController(entities, relations, model_id)
        # 应用推理规则
        results = reasoner.get_results()
        # 新建关系
        for i in results["new_relations"]:
            relation_data = RelationModel(
                source_id=i['source_id'],
                target_id=i['target_id'],
                type=i['type'],
                properties=i['properties'],
                model_id=i['model_id'],
            )
            kgController.create_relation(relation_data)
        return Success(data={"results": results})

    except Exception as e:
        logger.error(f"知识fail: {str(e)}")
        return Fail(msg="知识fail！")


# 自然语言处理算法

# 知识统计
@router.post("/nlp")
async def infer_transitive(
        model_id: str = Body(..., description="模型ID"),
        page: int = Body(1, description="页码"),
        page_size: int = Body(10, description="每页数量")
):
    try:
        entities = kgController.get_entities_by_model(model_id, page, page_size)
        relations = kgController.get_all_relations(model_id)
        graph_mining = GraphMiningAlgorithms(entities.data, relations)
        # 中心性指标

        centrality = graph_mining.calculate_centrality()
        degree_centrality_dict = {k: {k2: round(v2, 4) for k2, v2 in v.items()} for k, v in centrality.items() if
                                  k == "closeness_centrality"}
        for k, v in enumerate(degree_centrality_dict["closeness_centrality"]):
            merged_properties = {
                "properties": {
                    "closeness_centrality": degree_centrality_dict["closeness_centrality"][v]
                }
            }
            kgController.update_entity(v, merged_properties)



        return Success(data={
            "results": {k: {k2: round(v2, 4) for k2, v2 in v.items()} for k, v in centrality.items()},
        })

    except Exception as e:
        logger.error(f"graph: {str(e)}")
        return Fail(msg="graph！")


# 知识统计
@router.post("/stat")
async def infer_transitive(
        model_id: str = Body(..., description="模型ID"),
        page: int = Body(1, description="页码"),
        page_size: int = Body(10, description="每页数量")
):
    try:
        entities = kgController.get_entities_by_model(model_id, page, page_size)
        relations = kgController.get_all_relations(model_id)

        reasoner = KnowledgeCalculateController(entities, relations, model_id)
        stats_result = reasoner.calculate_statistics()
        print(json.dumps(stats_result, indent=2, ensure_ascii=False))

        return Success(data={"results": stats_result})

    except Exception as e:
        logger.error(f"stat: {str(e)}")
        return Fail(msg="stat！")


# 知识统计
@router.post("/graph")
async def infer_transitive(
        model_id: str = Body(..., description="模型ID"),
        page: int = Body(1, description="页码"),
        page_size: int = Body(10, description="每页数量")
):
    try:
        entities = kgController.get_entities_by_model(model_id, page, page_size)
        relations = kgController.get_all_relations(model_id)
        graph_mining = GraphMiningAlgorithms(entities.data, relations)
        # 中心性指标

        centrality = graph_mining.calculate_centrality()
        degree_centrality_dict = {k: {k2: round(v2, 4) for k2, v2 in v.items()} for k, v in centrality.items() if
                                  k == "degree_centrality"}
        for k, v in enumerate(degree_centrality_dict["degree_centrality"]):
            merged_properties = {
                "properties": {
                    "degree_centrality": degree_centrality_dict["degree_centrality"][v]
                }
            }
            kgController.update_entity(v, merged_properties)

        # 社区检测
        communities = graph_mining.detect_communities()
        for k, v in enumerate(communities["partition"]):
            print(v, communities["partition"][v])
            merged_properties = {
                "properties": {
                    "community_partition": communities["partition"][v]
                }
            }
            kgController.update_entity(v, merged_properties)

        return Success(data={
            "results": {k: {k2: round(v2, 4) for k2, v2 in v.items()} for k, v in centrality.items()},
            "community": communities
        })

    except Exception as e:
        logger.error(f"graph: {str(e)}")
        return Fail(msg="graph！")



'''
实体部分的融合和关系融合 后期可能会用上
'''

# 实体属性融合  自主model获取所有实体，对比相同name的实体，进行属性的融合
@router.post("/fusion/graph/entity/")
async def infer_transitive(
        model_id: str = Body(..., description="模型ID"),
        page: int = Body(1, description="页码"),
        page_size: int = Body(100, description="每页数量")
):
    # try:
    entities = kgController.get_entities_by_model(model_id, page, page_size)
    relations = kgController.get_all_relations(model_id)

    reasoner = KnowledgeCalculateController(entities, relations, model_id)
    # 应用推理规则
    results = reasoner.merge_entities()
    # 更新实体
    for i in results.data:
        update_data = {
            "properties": i.properties
        }
        kgController.update_entity(i.id, update_data)
    return EntityModelList(msg="success", data=results)

    # except Exception as e:
    #     logger.error(f"知识fail: {str(e)}")
    #     return Fail(msg="知识fail！")



# 关系融合  自主model获取所有实体，对比相同text的实体，进行关系的融合
@router.post("/fusion/relation")
async def infer_transitive(
        model_id: str = Body(..., description="模型ID"),
        page: int = Body(1, description="页码"),
        page_size: int = Body(100, description="每页数量")
):
    # try:
    entities = kgController.get_entities_by_model(model_id, page, page_size)
    relations = kgController.get_all_relations(model_id)

    reasoner = KnowledgeCalculateController(entities, relations, model_id)
    # 应用推理规则
    results = reasoner.find_and_create_new_relations()
    # 新建关系
    for i in results:
        kgController.create_relation(i)
    return results

    # except Exception as e:
    #     logger.error(f"知识fail: {str(e)}")
    #     return Fail(msg="知识fail！")


import asyncio

from fastapi import APIRouter, Depends, Query, HTTPException, Request
from app.services.nlp_service import NLPService
from app.services.neo4j_service import neo4j_service
from app.services.es_service import es_service
from loguru import logger
from app.schemas.kg import EntityRequest, RelationRequest
from app.schemas.base import Fail, Success
from app.schemas.graph import RelationCreate, BulkRelationCreate
from typing import List, Dict
from fastapi import APIRouter, Query, Body, Path, Depends

from app.core.dependency import get_nlp_service
from app.utils import fusion
from app.controllers.knowledge_graph import knowledgeGraphController as kgController
from app.controllers.kg import KGListController
import uuid
from app.schemas.knowledge_graph import EntityModel, RelationModel
from app.schemas.knowledge_merge import EntityRepairRequest

from concurrent.futures import ThreadPoolExecutor
# from concurrent.futures import ProcessPoolExecutor
executor = ThreadPoolExecutor(max_workers=4)

router = APIRouter()

# 用于存储任务状态的全局字典
task_status = {}


@router.post("/entities/inctest")
async def get_entity(nlp_service: NLPService = Depends(get_nlp_service)):
    kafka_data_list = [
        # 原有数据（略作调整，增加属性）
        {'text': '和邓颖超在结婚前，周恩来因公务繁忙派人去车站接邓，结果没有接到，邓颖超自己找到。周恩来,生于1898年，职业是政治家。', 'source': 'kafka'},
        {'text': '万劫谷石屋外段延庆获救，并暗助黄眉僧，吸取部份段誉内力。段誉生于1083年，职业是大理国太子。', 'source': 'kafka'},
        {'text': '、侯宝林）、开场小唱（郭启儒、刘宝瑞、郭全宝、郭启儒）、空城计。侯宝林住在北京市，职业是相声演员。', 'source': 'kafka'},
        #
        {'text': '张三是李四的父亲，今年50岁，职业是医生。张三住在上海，爱好是钓鱼。', 'source': 'kafka'},
        {'text': '《红楼梦》是曹雪芹创作的古典小说，曹雪芹生于1715年，出身于贵族家庭。曹雪芹住在南京，爱好是写诗。', 'source': 'kafka'},
        {'text': '刘德华和梁朝伟在电影《无间道》中合作，刘德华饰演警察，梁朝伟饰演卧底。刘德华，出生于1961年，职业是演员。', 'source': 'kafka'},
        {'text': '张嘉译是赵六的导师，张嘉译今年45岁，拥有博士学位。张嘉译住在杭州，爱好是读书。', 'source': 'kafka'},
        {'text': '李雷和韩梅梅是夫妻，李雷今年30岁，是一名工程师。李雷住在北京，爱好是打篮球。', 'source': 'kafka'}
    ]
    attr = await  nlp_service.extract_attributes_with_rules("张嘉译是赵六的导师，张嘉译今年45岁，拥有博士学位。张嘉译住在杭州，爱好是读书。", "张嘉译")
    return attr


@router.post("/entity")
async def get_entity(entire: EntityRequest, nlp_service: NLPService = Depends(get_nlp_service), ):
    try:
        sentence = entire.sentence
        # logger.info(f"正在识别实体: {sentence}")
        entities = await nlp_service.extract_entities(sentence)

        # logger.success(f"实体识别成功: {entities}")
        return Success(data=entities)


    except Exception as e:
        logger.error(f"识别实体失败: {str(e)}")
        return Fail(msg="识别实体失败！" + str(e))


# 识别多条数据实体，关系 写入图谱基础数据
@router.post("/entities")
async def get_entity(entities: Request, nlp_service: NLPService = Depends(get_nlp_service),
                     ):
    try:
        raw_json = await entities.json()
        logger.info(f"正在识别实体和关系: {raw_json}")
        all_relations = []
        users_data = []
        for item in raw_json:
            text = item["text"]
            entities = await nlp_service.extract_entities(text)
            relations = await nlp_service.extract_all_relations(text, entities)
            all_relations.extend(relations)
            logger.debug(f"获得关系: {relations}")

            filtered_users = [
                {"name": ent[0], "email": f"{ent[0].lower()}@example.com"}
                for ent in entities
                if ent[1] == "PERSON" and 1 < len(ent[0]) < 4
            ]
            users_data.extend(filtered_users)

        # 1. 批量写入 ES
        result = await es_service.bulk_create_documents(
            "entity", users_data)

        logger.info(f"bulk_create_documents: {result}")

        # 2. 转换为Neo4j写入格式
        neo4j_relations = [
            RelationCreate(
                head=rel["head"],
                tail=rel["tail"],
                relation_type=rel["relation"],
                text=rel["text"]
            )
            for rel in all_relations
        ]

        # 3. 批量写入Neo4j
        result = await neo4j_service.bulk_create_relations(
            BulkRelationCreate(relations=neo4j_relations)
        )

        return Success(data={
            "status": "success",
            "processed_texts": len(raw_json),
            "relations_created": result["count"]
        })

    except Exception as e:
        logger.error(f"实体流fail: {str(e)}")
        return Fail(msg="实体流fail！" + str(e))


@router.post("/entities/inc")
async def get_entity(model_id: str = Query(...), nlp_service: NLPService = Depends(get_nlp_service)):
    query = {
        "query": {
            "match_all": {}
        },
        "_source": ["text"],
        "from": 0,  # 起始位置
        "size": 15  # 每页大小
    }
    result = await es_service.search_documents("remote_data", query)

    data_list = [{"text": hit["_source"]['text'], "source": "elasticsearch"} for hit in result]
    # 先模拟kafka 导入
    kafka_data_list = [
        # 原有数据（略作调整，增加属性）
        {'text': '和邓颖超在结婚前，周恩来因公务繁忙派人去车站接邓，结果没有接到，邓颖超自己找到。周恩来,生于1898年，职业是军事家。', 'source': 'kafka'},
        {'text': '万劫谷石屋外段延庆获救，并暗助黄眉僧，吸取部份段誉内力。段誉生于1083年，职业是大理国太子。', 'source': 'kafka'},
        {'text': '、侯宝林）、开场小唱（郭启儒、刘宝瑞、郭全宝、郭启儒）、空城计。侯宝林住在北京市，职业是相声演员。', 'source': 'kafka'},
        {'text': '张三是李四的父亲，今年50岁，职业是医生。张三住在上海，爱好是钓鱼。', 'source': 'kafka'},
        {'text': '《红楼梦》是曹雪芹创作的古典小说，曹雪芹生于1714年，出身于贵族家庭。曹雪芹住在南京，爱好是唱戏。', 'source': 'kafka'},
        {'text': '刘德华和梁朝伟在电影《无间道》中合作，刘德华饰演警察，梁朝伟饰演卧底。刘德华，出生于1961年，职业是歌手。', 'source': 'kafka'},
        {'text': '张嘉译是赵六的导师，张嘉译今年35岁，拥有博士学位。张嘉译住在杭州，爱好是写作。', 'source': 'kafka'},
        {'text': '李雷和韩梅梅是父子，李雷今年35岁，是一名工程师。李雷住在北京，爱好是打篮球。', 'source': 'kafka'}
    ]

    all_data = data_list + kafka_data_list

    # 2. 生成唯一的task_id
    task_id = str(uuid.uuid4())
    logger.info(f"提交任务: 生成task_id: {task_id}")  # 添加日志

    # 3. 初始化任务状态为 PENDING
    task_status[task_id] = {
        "status": "PENDING",
        "percent": 0,

        "message": "任务已提交，等待处理..."
    }
    logger.info(f"任务状态已初始化: task_id={task_id}, 状态=PENDING")  # 添加日志

    # 后台提交任务，立即返回
    executor.submit(process_entity_graph_sync, model_id, all_data, nlp_service, task_id)
    logger.info(f"任务已提交到线程池: task_id={task_id}")  # 添加日志

    # 5. 立即返回，告知用户任务已提交
    return Success(msg="建图任务已提交后台执行", data={"task_id": task_id})


def process_entity_graph_sync(model_id: str, data_list: List[Dict[str, str]], nlp_service: NLPService, task_id: str):
    try:
        total = len(data_list)
        task_status[task_id] = {
            "status": "RUNNING",
            "percent": 0,
            "message": "任务正在处理中..."
        }

        logger.info(f"任务 {task_id} 状态更新为 RUNNING")  # 添加日志

        all_relations = []
        all_entity = []
        users_data = []

        for idx, v in enumerate(data_list):
            try:
                text = v["text"]
                logger.info(f"识别 {text}")
                source = v["source"]
                entities = asyncio.run(nlp_service.extract_entities(text))  # 实际为同步调用
                entities = list(set(entities))
                all_entity.append(entities)
                logger.info(f"entities {entities}")
                logger.info(f"all_entity {all_entity}")

                relations = asyncio.run(nlp_service.extract_all_relations(text, entities, source))
                all_relations.extend(relations)
                logger.info(f"relations {relations}")

                for ent in entities:
                    if ent[1] == "PERSON" and 1 < len(ent[0]) < 4:
                        # 补充属性
                        attr = asyncio.run(nlp_service.extract_attributes_with_rules(text, ent[0]))
                        logger.info(f"attr {attr}")
                        properties = {"source": source, "text": text}
                        if len(attr) > 0:
                            properties.update(attr[0])
                        logger.info(f"properties {properties}")
                        users_data.append({"name": ent[0], "properties": properties})
            except Exception as e:
                print(f"处理文本失败: {e}")
            # ✅ 更新进度百分比
            percent = int((idx + 1) / total * 100)
            task_status[task_id]["percent"] = percent
            task_status[task_id]["message"] = f"已处理 {idx + 1}/{total} 条文本（{percent}%）"
            logger.info(f"任务 {task_id} 进度：{percent}%")

        users_with_uuid = []
        for user in users_data:
            user_id = str(uuid.uuid4())
            users_with_uuid.append(EntityModel(
                id=user_id,
                properties=user["properties"],
                name=user["name"])
            )
        logger.info(f"创建实体 ")

        # 创建实体
        kgController.create_bulk_entities(model_id, users_with_uuid)
        logger.info(f"创建实体完成 ")

        # 构建name到id的映射
        name_to_id = {item.name + item.properties["text"] + item.properties["source"]: item.id for item in
                      users_with_uuid}

        # 创建关系
        for relation in all_relations:
            head = relation["head"] + relation["text"] + relation["source"]
            tail = relation["tail"] + relation["text"] + relation["source"]
            if head in name_to_id and tail in name_to_id:
                updated_relation = RelationModel(
                    source_id=name_to_id[head],
                    target_id=name_to_id[tail],
                    type=relation["relation"],
                    properties={
                        "text": relation["text"],
                        "source": relation["source"],
                    },
                    model_id=model_id
                )
                kgController.create_relation(updated_relation)
                # 更新任务状态为 SUCCESS

        # 查询entity 、 entity_relations 是否有

        entity_result = es_service.index_exists("entity")
        entity_relations_result = es_service.index_exists("entity_relations")

        #  批量写入 ES 实体
        if not entity_result:
            es_service.bulk_create_documents(
                "entity", users_data)
        else:
            print("已经存在实体")

        #  批量写入 ES 关系
        if not entity_relations_result:
            es_service.bulk_create_documents_old(
                "entity_relations", all_relations)
        else:
            print("已经存在关系")

        task_status[task_id] = {
            "status": "SUCCESS",
            "message": "任务处理完成"
        }

        logger.info(f"任务 {task_id} 状态更新为 SUCCESS")  # 添加日志

    except Exception as e:
        # 更新任务状态为 FAILURE，并记录错误信息
        task_status[task_id] = {
            "status": "FAILURE",
            "message": f"任务处理失败: {str(e)}"
        }
        logger.error(f"任务 {task_id} 处理失败: {str(e)}")


@router.get("/tasks")
async def get_task_status(task_id: str = Query(),
                          ):
    """
    查询指定任务的状态
    """
    if task_id not in task_status:
        raise HTTPException(status_code=404, detail="任务ID不存在")

    status_info = task_status[task_id]
    return {
        "task_id": task_id,
        "percent": status_info.get("percent", 0),  # 如果 "percent" 不存在，默认返回 0
        "status": status_info["status"],
        "message": status_info["message"]
        # 如果需要返回更多信息，可以在此扩展
    }


@router.post("/relation")
async def get_relation(relation: RelationRequest, nlp_service: NLPService = Depends(get_nlp_service), ):
    try:
        sentence = relation.sentence
        entity1 = relation.entity1
        entity2 = relation.entity2
        logger.info(f"正在识别实体关系: {sentence, entity1, entity2}")
        relation = await nlp_service.extract_relations(sentence, entity1, entity2)

        logger.success(f"实体识别关系成功: {relation}")
        return Success(data={"relation": relation})

    except Exception as e:
        logger.error(f"识别实体关系失败: {str(e)}")
        return Fail(msg="识别实体关系失败！")


# @router.post("/disambiguation_ai")
# async def disambiguation(entire: EntityRequest, nlp_service: NLPService = Depends(get_nlp_service), ):
#     try:
#         text = entire.sentence
#         # Apple is headquartered in Cupertino 测试数据
#
#         results = await nlp_service.disambiguation(text)
#
#         return Success(data={"results": results})
#
#
#     except Exception as e:
#         logger.error(f"实体消歧fail: {str(e)}")
#         return Fail(msg="实体消歧fail！")


# 实体列表获取
@router.get("/entity/list")
async def entity_list(
        name: str = None,
        index: str = "entity",
        page: int = Query(1, ge=1, description="页码，从1开始"),  # 默认第1页，最小值为1
        pagesize: int = Query(10, ge=1, le=100, description="每页大小，范围1-100")):
    try:
        # 查询 ES
        # 计算 Elasticsearch 的 from 参数
        from_ = (page - 1) * pagesize
        # 构建查询DSL
        query = {
            "from": from_,  # 起始位置
            "size": pagesize  # 每页大小
        }

        # 如果提供了name参数，则添加match_phrase查询
        if name is not None:
            query["query"] = {
                "match_phrase": {
                    "name": name
                }
            }
        else:
            # 如果没有name参数，查询所有文档
            query["query"] = {"match_all": {}
                              }

        result = await es_service.search_documents_total(
            index, query)

        total = result["total"]
        hits = result["hits"]
        total_pages = (total + pagesize - 1) // pagesize

        # 提取 _id 和 _source 组合成新的字典
        data_list = [
            {
                "_id": hit["_id"],  # Elasticsearch 分配的文档 ID
                **hit["_source"]  # 文档的原始数据（name, email 等）
            }
            for hit in hits
        ]

        return Success(data={
            "data": data_list,
            "pagination": {
                "total": total,
                "total_pages": total_pages,
                "current_page": page,
                "page_size": pagesize,
                "has_next": page < total_pages,
                "has_prev": page > 1
            }
        })

    except Exception as e:
        logger.error(f"实体列表获取fail: {str(e)}")
        return Fail(msg="实体列表获取fail！")


# 实体属性融合  es-list 获取所有实体，对比相同name的实体，进行属性的融合
@router.post("/fusion/entity")
async def infer_transitive(
):
    try:
        from_ = 0
        # 构建查询DSL
        query = {
            # "_source": [""],
            "from": from_,  # 起始位置
            "size": 200,  # 每页大小
            "query": {
                "match_all": {}
            }
        }

        result = await es_service.search_documents(
            "entity", query)

        reasoner = KGListController()
        results = reasoner.merge_and_filter_es_entities(result)

        es_service.bulk_full_update_documents(results, index="entity")
        print(results)
        return Success(data={"results": results})

    except Exception as e:
        logger.error(f"实体属性融合fail: {str(e)}")
        return Fail(msg="实体属性融合！")


# 实体关系融合  es-list 获取所有关系，对比相同对的实体，进行属性的融合
@router.post("/fusion/relations")
async def fusion_relations():
    try:
        from_ = 0
        # 构建查询DSL
        query = {
            # "_source": [""],
            "from": from_,  # 起始位置
            "size": 200,  # 每页大小
            "query": {
                "match_all": {}
            }
        }

        result = await es_service.search_documents(
            "entity_relations", query)

        # 提取 _id 和 _source 组合成新的字典
        data_list = [
            {
                "_id": hit["_id"],  # Elasticsearch 分配的文档 ID
                **hit["_source"]  # 文档的原始数据（name, email 等）
            }
            for hit in result
        ]

        reasoner = KGListController()
        results = reasoner.merge_relations(data_list)

        es_service.bulk_full_update_relations(results, index="entity_relations")
        return Success(data={"results": results})

    except Exception as e:
        logger.error(f"实体关系融合fail: {str(e)}")
        return Fail(msg="实体关系融合fail！")


# 实体消岐
@router.post("/disambiguation")
async def fusion_relations(entity_json: EntityRepairRequest, ):
    try:
        # 合并 es id ，除了id的都消岐
        res = es_service.delete_merge(entity_json.entity_id, entity_json.entity_list)

        return Success(data=res)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"消岐失败：{e}")

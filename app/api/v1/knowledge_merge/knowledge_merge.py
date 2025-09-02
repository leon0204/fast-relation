import logging
import os
import random
import uuid

import pycorrector
from fastapi import APIRouter, Query, Depends, Body
from fastapi.exceptions import HTTPException

from app.controllers.knowledge_merge import knowledgeMergeController as mergeController
from app.controllers.knowledge_graph import knowledgeGraphController as kgController
from app.schemas.base import Fail, Success
from app.schemas.knowledge_merge import EntityRepairRequest, QueryRequest, LinkRequest
from app.services.nlp_service import NLPService
from app.core.dependency import get_nlp_service
from app.schemas.knowledge_graph import EntityModel, RelationModel, EntityUpdateRequest

logger = logging.getLogger(__name__)

from app.services.text_correct import TextCorrectionService  # 导入服务类

# 初始化服务（全局单例）
text_correction_service = TextCorrectionService()

from concurrent.futures import ThreadPoolExecutor

executor = ThreadPoolExecutor(max_workers=4)

import asyncio

router = APIRouter()


@router.get("/alignment", summary="本体对齐获取列表")
def get_entity_alignment(
        entity: str = Query(..., description="实体name"),
        entity_id: str = Query(..., description="实体id"),
        model_id: str = Query(..., description="模型ID"),
        page: int = Query(1, description="页码"),
        page_size: int = Query(10, description="每页数量"),
):
    """获取指定知识图谱模型下的所有实体列表。"""
    try:
        page_size = 100
        entities = kgController.get_entities_by_model(model_id, page, page_size)
        # 1 基于去除重复实体
        # 2 基于别名替换
        # 3 基于字符串相似度>80%

        unique_entities = mergeController.remove_duplicate_entities(entity, entity_id, entities)

        # print("unique_entities is ", unique_entities)

        return Success(data=unique_entities)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"本体对齐失败：{e}")


'''
对齐不同本体中的概念/实体(建立映射关系)
合并多实体/相似度/别名/修正
'''


@router.post("/repair", summary="本体对齐修正")
def post_entity_repair(entity_json: EntityRepairRequest, ):
    try:
        # 合并
        kgController.merge_entities(entity_json.entity_id, entity_json.entity_list)

        return Success()

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"本体对齐修正失败：{e}")


'''
消岐 直接合到指定id 
合并多实体/相似度/别名/修正
'''


@router.post("/disambiguation", summary="本体对齐修正")
def post_entity_repair(entity_json: EntityRepairRequest, ):
    try:
        # 合并
        kgController.merge_entities(entity_json.entity_id, entity_json.entity_list)

        return Success()

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"本体对齐修正失败：{e}")


'''
基于自然语言分析，对输入的【文本】的提及链接到知识库的【具体实体】
或产生新的实体与当前实体链接 
'''


@router.post("/link", summary="实体链接")
async def post_entity_repair(link_json: LinkRequest, nlp_service: NLPService = Depends(get_nlp_service)):
    try:
        all_relations = []
        users_data = []

        text = link_json.sentence
        model_id = link_json.model_id
        entities = await nlp_service.extract_entities(text)
        print("entities 开始", entities)
        entities = list(set(entities))
        relations = await nlp_service.extract_all_relations(text, entities)
        all_relations.extend(relations)
        print(entities, relations)

        for ent in entities:
            if ent[1] == "PERSON" and 1 < len(ent[0]) < 4:
                users_data.append({"name": ent[0]})

        users_with_uuid = []
        insert_list = []
        for user in users_data:
            user_id = str(uuid.uuid4())
            users_with_uuid.append(EntityModel(id=user_id, name=user["name"]))

        print("users_with_uuid 最初", users_with_uuid)
        # 得先查询是否有对应得实体 ，有则替换现存关系
        exist_entities = kgController.get_entities_by_model(model_id, 1, 1000)
        print(exist_entities.data)

        # 创建一个字典，以实体名称为键，实体ID为值，方便快速查找
        exist_entity_dict = {entity.name: entity.id for entity in exist_entities.data}
        print("exist_entity_dict ", exist_entity_dict)

        # 遍历 users_with_uuid 列表，替换同名实体的ID
        for user in users_with_uuid:
            if user.name in exist_entity_dict:
                # 如果存在同名实体，则替换ID
                # 可选：打印日志
                print(f"替换实体ID: 名称 '{user.name}' 的ID从 {user.id} 更新为 {exist_entity_dict[user.name]}")
                user.id = exist_entity_dict[user.name]
            else:
                insert_list.append(EntityModel(id=user.id, name=user.name))

        print(users_with_uuid)
        print(insert_list)

        # 创建实体
        kgController.create_bulk_entities(model_id, insert_list)
        # 构建name到id的映射
        name_to_id = {item.name: item.id for item in users_with_uuid}

        # 获取当前的关系
        exist_relationss = kgController.get_all_relations(model_id)

        # 创建关系
        for relation in all_relations:
            exists = False
            if relation["head"] in name_to_id and relation["tail"] in name_to_id:
                updated_relation = RelationModel(
                    source_id=name_to_id[relation["head"]],
                    target_id=name_to_id[relation["tail"]],
                    type=relation["relation"],
                    properties={"text": relation["text"]},
                    model_id=model_id
                )
                for rel in exist_relationss:
                    if rel.source_id == updated_relation.source_id and rel.target_id == updated_relation.target_id and rel.type == updated_relation.type:
                        exists = True
                        break
                if not exists:
                    # print(updated_relation)
                    kgController.create_relation(updated_relation)

        return Success()

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"实体链接失败：{e}")


# 知识问答
@router.post("/ask", summary="知识问答")
async def post_entity_ask(question: QueryRequest, nlp_service: NLPService = Depends(get_nlp_service)):
    # try:
    '''
    1 关键字 判断用户问的是 name 查找 ｜ 关系查找 ｜ 属性查找   check_words
    2 返回 链路
    '''
    question = question.question.strip()
    if not question:
        raise HTTPException(status_code=400, detail="问题不能为空")

    logger.info(f"收到查询请求: {question}")

    query_type = mergeController.detect_query_type(question)
    logger.info(f"收到查询 query_type: {query_type}")
    entities = await nlp_service.extract_entities(question)
    # print("提取到，entities",entities)
    # relations = await nlp_service.extract_all_relations(question, entities)
    if query_type == "name":

        result = kgController.query_by_name(question, entities)
    elif query_type == "relation":
        result = kgController.query_relationship(question, entities)
    elif query_type == "property":
        result = kgController.query_by_property(question, entities)
    else:
        result = {"error": "无法识别的查询类型"}

    result = mergeController.format_query_result(query_type, result)

    logger.info(f"查询完成: {query_type}, 结果数量: {len(result)}")

    return Success(data={
        "type": query_type,
        "result": result
    }
    )

    # except Exception as e:
    #     raise HTTPException(status_code=500, detail=f"问答失败：{e}")


# 知识问答list
@router.get("/ask/list", summary="知识问答list")
async def get_ask_list():
    # try:
    '''
    增加文档，知识问答list
    '''
    entitys = kgController.query_frequent_entity()
    entitys = [entity["name"] for entity in entitys]
    relations = kgController.query_frequent_relation(entitys)

    relation_keyword = random.choice(mergeController.CHECK_WORDS["relation"])

    entity_res = [entity + "的信息" for entity in entitys]

    # 去重处理
    unique_relations = []
    seen = set()

    for relation in relations:
        # 创建一个元组作为唯一标识
        relation_key = (relation["source_name"], relation["target_name"])

        # 如果这个关系组合还没出现过
        if relation_key not in seen:
            seen.add(relation_key)
            unique_relations.append(relation)

    # print("unique_relations is ",unique_relations)
    relations_res = []
    for rel in unique_relations:
        source_name = rel["source_name"]
        target_name = rel["target_name"]
        if source_name and target_name:
            relations_res.append(rel["source_name"] + "和" + rel["target_name"] + "的" + relation_keyword)

    # relations_res = [rel["source_name"] + "和" + rel["target_name"] + "的" + relation_keyword for rel in
    #                  unique_relations]

    # 合并两个数组

    # 随机选择10个元素(如果总数不足10个，则返回全部)
    entity_selection = random.sample(entity_res, min(5, len(entity_res)))
    relation_selection = random.sample(relations_res, min(5, len(relations_res)))
    combine_selection = random.sample(entity_selection + relation_selection,
                                      min(10, len(entity_selection + relation_selection)))

    return Success(data={
        "data": combine_selection,
    })

    # except Exception as e:
    #     raise HTTPException(status_code=500, detail=f"知识问答list：{e}")


# 情感分析list
@router.get("/analyzer/list", summary="情感分析list")
async def get_ask_list():
    # try:
    '''
    增加文档，知识问答list
    '''
    entitys = kgController.query_frequent_entity()
    entitys = [entity["name"] for entity in entitys]
    relations = kgController.query_frequent_relation(entitys)

    relation_keyword = random.choice(mergeController.CHECK_WORDS["relation"])

    # entity_res = [entity + "是谁" for entity in entitys]

    # 去重处理
    unique_relations = []
    seen = set()

    for relation in relations:
        # 创建一个元组作为唯一标识
        relation_key = (relation["source_name"], relation["target_name"], relation["relation_type"])

        # 如果这个关系组合还没出现过
        if relation_key not in seen:
            seen.add(relation_key)
            unique_relations.append(relation)

    print("unique_relations is", unique_relations)

    relations_res = []
    for rel in unique_relations:
        source_name = rel["source_name"]
        target_name = rel["target_name"]
        if source_name and target_name and source_name != target_name:
            relations_res.append(rel["source_name"] + "和" + rel["target_name"] + "的" + relation_keyword)

    relation_selection = random.sample(relations_res, min(5, len(relations_res)))

    return Success(data={
        "data": relation_selection,
    })

    # except Exception as e:
    #     raise HTTPException(status_code=500, detail=f"知识问答list：{e}")


# 搜索引擎list
@router.get("/search/list", summary="智能引擎list")
async def get_search_list():
    search_list = [
        "中国科学家有哪些",
        "中国科学家奖项有哪些",
        "杂交水稻之父是谁",
        "头衔查询",
        "谁发明了青蒿素",
        "袁隆平",
        "阿里巴巴集团创始人",
    ]
    return Success(data={
        "data": search_list,
    })


# 智能搜索引擎
@router.post("/search", summary="智能搜索引擎")
async def post_search(question: QueryRequest, ):
    try:
        '''
        增加文档，提供引擎搜索
        '''
        question = question.question.strip()
        if not question:
            raise HTTPException(status_code=400, detail="问题不能为空")

        logger.info(f"search info: {question}")

        results = kgController.search(question)
        # print(results)
        results = kgController.assemble_compatible_search_result(results)

        return Success(data={
            "answer": results
        })

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"问答失败：{e}")


# 智能搜索引擎
@router.post("/analyzer", summary="情感分析")
async def post_analyzer(question: QueryRequest, nlp_service: NLPService = Depends(get_nlp_service)):
    # try:
    '''
    增加文档，提供analyzer
    '''
    question = question.question.strip()
    if not question:
        raise HTTPException(status_code=400, detail="问题不能为空")

    logger.info(f"search info: {question}")
    entities = await nlp_service.extract_entities(question)
    logger.info(f"search entities: {entities}")

    result = kgController.query_relationship(question, entities)
    if len(result) <= 0:
        raise HTTPException(status_code=400, detail="未找到相关的关系")
    # print(result)
    # print(result[0])
    result_data = mergeController.format_query_result("relation", result)
    # print(result_data)
    analyzer = mergeController.analyze_relation(result[0]["relation_type"])

    return Success(data={
        "result": result_data,
        "analyzer": analyzer
    })

    # except Exception as e:
    #     raise HTTPException(status_code=500, detail=f"问答失败：{e}")


# 智能搜索引擎
@router.post("/search_init", summary="智能搜索引擎init")
async def post_search_init():
    try:
        '''
        增加文档，提供引擎搜索 
        '''
        kgController.add_document(
            title="鲁迅",
            content="""鲁迅是中国著名文学家、思想家、革命家、教育家、民主战士，新文化运动的重要参与者，中国现代文学的奠基人之一。1881年生于浙江绍兴，原名周树人，"鲁迅"是他1918年发表《狂人日记》时所用的笔名。他以笔为武器，深刻批判封建礼教和社会弊病，创作了《呐喊》《彷徨》《朝花夕拾》等经典作品，对中国现代文学发展产生深远影响。1936年病逝于上海。""",
            entities=[
                {"name": "鲁迅", "type": "文学家"},
                {"name": "周树人", "type": "本名"},
                {"name": "狂人日记", "type": "文学作品"},
                {"name": "呐喊", "type": "文学作品"},
                {"name": "彷徨", "type": "文学作品"},
                {"name": "朝花夕拾", "type": "文学作品"},
                {"name": "新文化运动", "type": "历史运动"},
                {"name": "浙江绍兴", "type": "出生地"},
                {"name": "上海", "type": "逝世地"}
            ],
            person_info={
                "name": "鲁迅",
                "birth_year": 1881,
                "death_year": 1936,
                "nationality": "中国",
                "achievements": [
                    {"name": "新文化运动先驱", "year": 1915},
                    {"name": "《狂人日记》发表", "year": 1918},
                    {"name": "《呐喊》出版", "year": 1923},
                    {"name": "《彷徨》出版", "year": 1926},
                    {"name": "《朝花夕拾》出版", "year": 1928}
                ],
                "related_events": [
                    {"name": "赴日学医", "year": 1902},
                    {"name": "弃医从文", "year": 1906},
                    {"name": "发表《狂人日记》", "year": 1918},
                    {"name": "参与新文化运动", "year": 1915},
                    {"name": "逝世于上海", "year": 1936}
                ]
            }
        )
        kgController.add_document(
            title="钱学森",
            content="""钱学森是中国著名科学家，被誉为"中国航天之父"。1911年生于上海，1935年赴美留学，
                        1955年回国效力。他是中国导弹和航天事业的奠基人，两弹一星功勋奖章获得者。""",
            entities=[
                {"name": "钱学森", "type": "科学家"},
                {"name": "中国航天", "type": "科技领域"},
                {"name": "两弹一星", "type": "科技成就"},
                {"name": "美国", "type": "国家"},
                {"name": "上海", "type": "城市"}
            ],
            person_info={
                "name": "钱学森",
                "birth_year": 1911,
                "death_year": 2009,
                "nationality": "中国",
                "achievements": [
                    {"name": "中国导弹之父", "year": 1956},
                    {"name": "两弹一星功勋奖章", "year": 1999}
                ],
                "related_events": [
                    {"name": "回国效力", "year": 1955},
                    {"name": "中国第一颗人造卫星发射", "year": 1970}
                ]
            }
        )

        # 2. 添加袁隆平信息
        kgController.add_document(
            title="袁隆平",
            content="""袁隆平是中国杂交水稻育种专家，被誉为"杂交水稻之父"。1930年生于北京，
                        他成功研发出杂交水稻技术，为解决中国粮食问题作出巨大贡献，2004年获世界粮食奖。""",
            entities=[
                {"name": "袁隆平", "type": "农业科学家"},
                {"name": "杂交水稻", "type": "农业科技"},
                {"name": "世界粮食奖", "type": "奖项"},
                {"name": "北京", "type": "城市"}
            ],
            person_info={
                "name": "袁隆平",
                "birth_year": 1930,
                "death_year": 2021,
                "nationality": "中国",
                "achievements": [
                    {"name": "杂交水稻之父", "year": 1970},
                    {"name": "世界粮食奖", "year": 2004}
                ],
                "related_events": [
                    {"name": "杂交水稻研究突破", "year": 1973},
                    {"name": "超级稻亩产突破", "year": 2011}
                ]
            }
        )

        # 3. 添加屠呦呦信息
        kgController.add_document(
            title="屠呦呦",
            content="""屠呦呦是中国药学家，2015年诺贝尔生理学或医学奖获得者。她从中医药古典文献中
                        获取灵感，发现了青蒿素，为全球疟疾治疗做出革命性贡献。""",
            entities=[
                {"name": "屠呦呦", "type": "药学家"},
                {"name": "青蒿素", "type": "药物"},
                {"name": "诺贝尔生理学或医学奖", "type": "奖项"},
                {"name": "中医药", "type": "医学体系"}
            ],
            person_info={
                "name": "屠呦呦",
                "birth_year": 1930,
                "death_year": None,
                "nationality": "中国",
                "achievements": [
                    {"name": "诺贝尔生理学或医学奖", "year": 2015},
                    {"name": "青蒿素发现者", "year": 1972}
                ],
                "related_events": [
                    {"name": "青蒿素临床试验", "year": 1972},
                    {"name": "诺贝尔奖颁奖", "year": 2015}
                ]
            }
        )

        # 4. 添加马云信息
        kgController.add_document(
            title="马云",
            content="""马云是中国企业家，阿里巴巴集团创始人。1964年生于浙江杭州，1999年创立阿里巴巴，
                        推动了中国电子商务的发展，2014年阿里巴巴在纽交所上市，创下当时全球最大IPO记录。""",
            entities=[
                {"name": "马云", "type": "企业家"},
                {"name": "阿里巴巴", "type": "公司"},
                {"name": "电子商务", "type": "产业"},
                {"name": "浙江杭州", "type": "城市"}
            ],
            person_info={
                "name": "马云",
                "birth_year": 1964,
                "death_year": None,
                "nationality": "中国",
                "achievements": [
                    {"name": "阿里巴巴创始人", "year": 1999},
                    {"name": "全球最大IPO记录", "year": 2014}
                ],
                "related_events": [
                    {"name": "阿里巴巴创立", "year": 1999},
                    {"name": "阿里巴巴纽交所上市", "year": 2014}
                ]
            }
        )

        return Success(data=1)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"问答失败：{e}")


#
# import kenlm
# model_path = "~/.pycorrector/datasets/zh_giga.no_cna_cmn.prune01244.klm"
# lm_model = kenlm.Model(model_path)  # 加载模型后得到的对象
# @router.post("/complete")
# def complete_text(question: QueryRequest, ) -> str:
#     """
#     """
#
#     # 确认模型路径存在
#
#     if not os.path.exists(os.path.expanduser(model_path)):
#         print("错误：模型文件不存在！请手动下载并放置到：")
#         print(os.path.expanduser(model_path))
#
#     # 测试模型是否能加载
#     lm_model = kenlm.Model(os.path.expanduser(model_path))
#     print(f"模型加载成功！N-gram阶数：{lm_model.order}")
#     print("测试评分：", lm_model.score("今天天气", bos=True, eos=True))  # 正常应输出-10到-50之间的值
#
#     text = question.question
#     """极简补全测试（强制补一个字）"""
#     candidates = ["好", "的", "是", "了"]
#     scores = [(word, lm_model.score(text + word)) for word in candidates]
#     best_word = max(scores, key=lambda x: x[1])[0]
#     print(text + best_word)
#
#
#     max_add_len = 5
#     current = question.question
#     for _ in range(max_add_len):
#         # 获取下一个最可能字符（扩展候选集）
#         candidates = list("的了是有在和要也把都这着")
#         next_char = max(candidates,
#                         key=lambda c: lm_model.score(current + c, bos=False, eos=False))
#
#         # 终止条件：遇到结束符或概率过低
#         if next_char in {"。", "！", "？"} or lm_model.score(current + next_char) < -10:
#             break
#         current += next_char
#     return current


#
# # 纠错 correct 大模型版本，卡顿 ，已调通
# @router.post("/correct1")
# def get_correct(
#         question: QueryRequest,
# ):
#     from transformers import AutoModelForCausalLM, AutoTokenizer
#     here = os.path.dirname(os.path.abspath(__file__))
#     checkpoint = os.path.join(here, '../../../pretrained_models/chinese-text-correction-1.5b')
#
#     device = "cpu"  # for GPU usage or "cpu" for CPU usage
#     tokenizer = AutoTokenizer.from_pretrained(checkpoint)
#
#
#
#     model = AutoModelForCausalLM.from_pretrained(checkpoint).to(device)
#
#
#     input_text = "文本纠错：\n"+question.question  # 直接使用原始文本
#
#     inputs = tokenizer(input_text, return_tensors="pt").to(device)
#     outputs = model.generate(**inputs, max_new_tokens=1024, temperature=0, do_sample=False, repetition_penalty=1.08)
#
#     print(tokenizer.decode(outputs[0], skip_special_tokens=True))
#


@router.post("/correct_big")
def get_correct(entity_id: str = Body(..., description="实体ID"),
                correct_k: str = Body(...),
                correct_v: str = Body(...)):
    """文本补全接口"""
    # 2. 生成唯一的task_id
    task_id = str(uuid.uuid4())
    logger.info(f"提交任务: 生成task_id: {task_id}")  # 添加日志

    # 3. 初始化任务状态为 PENDING
    task_status[task_id] = {
        "status": "PENDING",
        "percent": 0,
        "message": "任务已提交，任务正在处理中..."
    }
    logger.info(f"任务状态已初始化: task_id={task_id}, 状态=PENDING")  # 添加日志

    executor.submit(process_buquan_sync, entity_id, correct_k, correct_v, task_id)
    logger.info(f"任务已提交到线程池")
    return Success(msg="补全任务已提交后台执行", data={"task_id": task_id})




def process_buquan_sync(entity_id: str,
                        correct_k: str,
                        correct_v: str,
                        task_id: str
                        ):
    try:

        corrected_text = asyncio.run(text_correction_service.correct_text(correct_v))
        logger.info(f"corrected_text{corrected_text}")  # 添加日志

        merged_properties = {
            "properties": {
                correct_k: corrected_text
            }
        }
        kgController.update_entity(entity_id, merged_properties)
        logger.info(f"corrected_text {merged_properties}")

        task_status[task_id] = {
            "status": "SUCCESS",
            "percent": 100,
            "message": "任务处理完成"
        }
        # return Success(data={
        #     "corrected_text": corrected_text
        # })
    except Exception as e:
        logger.info(f"补全失败 {e}")

        # raise HTTPException(status_code=500, detail=f"补全失败：{e}")


# 用于存储任务状态的全局字典
task_status = {}




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



# 纠错 correct
@router.post("/correct")
def get_correct(
        entity_id: str = Body(..., description="实体ID"),
        correct_k: str = Body(...),
        correct_v: str = Body(...),

):
    # 2. 生成唯一的task_id
    task_id = str(uuid.uuid4())
    logger.info(f"提交任务: 生成task_id: {task_id}")  # 添加日志

    # 3. 初始化任务状态为 PENDING
    task_status[task_id] = {
        "status": "PENDING",
        "percent": 0,
        "message": "任务已提交，任务正在处理中..."
    }
    logger.info(f"任务状态已初始化: task_id={task_id}, 状态=PENDING")  # 添加日志

    executor.submit(process_correct_sync, entity_id, correct_k, correct_v, task_id)
    logger.info(f"任务已提交到线程池")
    return Success(msg="纠错任务已提交后台执行", data={"task_id": task_id})



def process_correct_sync(entity_id: str,
                         correct_k: str,
                         correct_v: str,
                         task_id: str
                         ):
    try:
        print("进入 process_correct_sync 函数")
        # logger.info(
        #     f"进入 process_correct_sync 函数，entity_id: {entity_id}, correct_k: {correct_k}, correct_v: {correct_v}")

        # logger.info(f"纠错 text {correct_v}")
        print("纠错", correct_v)
        corrector = pycorrector.Corrector()
        corrected_text = corrector.correct(correct_v)
        merged_properties = {
            "properties": {
                correct_k: corrected_text["target"]
            }
        }
        print("process_correct_sync", merged_properties)
        # logger.info(f"process_correct_sync {merged_properties}")

        kgController.update_entity(entity_id, merged_properties)
        print("update_entity", )

        task_status[task_id] = {
            "status": "SUCCESS",
            "percent": 100,
            "message": "任务处理完成"
        }

    # return Success(data={
    #     "corrected_text": corrected_text
    # })
    except Exception as e:
        print("纠错失败", e)
        # raise HTTPException(status_code=500, detail=f"纠错失败：{e}")


# 查询id model 下的所有 name 相似的，返回的属性，集合到这个id 下，调更新实体接口
@router.post("/update")
def get_correct(
        entity_id: str = Body(..., description="实体ID"),
        entity: str = Body(..., description="实体name"),
        model_id: str = Body(..., description="模型ID")):
    """文本纠错接口"""
    try:
        entities = kgController.get_entities_by_model(model_id, 1, 100)
        unique_entities = mergeController.remove_duplicate_entities(entity, entity_id, entities)

        print("unique_entities is ", unique_entities)
        removed_entities = unique_entities["removed_entities"]
        if len(removed_entities) > 0:
            # 合并properties（空值不覆盖）
            merged_properties = {}
            for entity in removed_entities:
                if not isinstance(entity.get('properties'), dict):
                    continue

                for key, new_value in entity['properties'].items():
                    # 仅当新值非空时覆盖（或字段不存在时添加）
                    if new_value or key not in merged_properties:
                        merged_properties[key] = new_value

            print("合并后的properties（空值不覆盖）:")
            print(merged_properties)
            # entity_update = EntityUpdateRequest(
            #     properties=merged_properties
            # )
            # update_data = entity_update.model_dump(exclude_unset=True)
            kgController.update_entity(entity_id, merged_properties)
            return Success(data={"info": "知识更新成功"})

        else:
            return Success(data={"info": "未找到可更新的知识"})

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"知识更新失败：{e}")


@router.post("/correct_big_old")
def get_correct(entity_id: str = Body(..., description="实体ID"),
                correct_k: str = Body(...),
                correct_v: str = Body(...)):
    """文本补全接口"""
    try:
        corrected_text = text_correction_service.correct_text(correct_v)
        merged_properties = {
            "properties": {
                correct_k: corrected_text
            }
        }
        kgController.update_entity(entity_id, merged_properties)
        return Success(data={
            "corrected_text": corrected_text
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"补全失败：{e}")


# 纠错 correct
@router.post("/correct_old")
def get_correct(
        entity_id: str = Body(..., description="实体ID"),
        correct_k: str = Body(...),
        correct_v: str = Body(...),

):
    corrector = pycorrector.Corrector()
    corrected_text = corrector.correct(correct_v)
    merged_properties = {
        "properties": {
            correct_k: corrected_text["target"]
        }
    }
    kgController.update_entity(entity_id, merged_properties)
    return Success(data={
        "corrected_text": corrected_text
    })

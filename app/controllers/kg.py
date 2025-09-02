import logging
import uuid

from fuzzywuzzy import fuzz

logger = logging.getLogger(__name__)
from typing import Dict, Optional, List, Tuple, Any
from app.schemas.knowledge_graph import KnowledgeGraphModel, ModelType, \
    KnowledgeGraphUpdateRequest, KnowledgeGraphModelListData, EntityModel, \
    RelationModel, EntityModelListData
from collections import defaultdict
import json
from collections import defaultdict
import networkx as nx
import pandas as pd
from typing import List, Dict, Any
from copy import deepcopy


class KGListController:
    """实体列表处理类"""

    def __init__(self):
        """
        :param entities: EntityModelListData 对象
        :param relations: RelationModel 列表
        """
        pass

        # self.entities_data = entities  # 保存原始数据对象
        # self.model_id = model_id  # 保存原始数据对象
        # self.relations_data = relations  # 保存原始关系列表


        # 将EntityModel对象转换为字典格式存储
        # self.entity_dict = {
        #     entity.id: entity.dict()  # 使用.dict()将Pydantic模型转为字典
        #     for entity in entities.data
        #     if entity.id is not None  # 确保id不为None
        # }
        #
        # for relation in relations:
        #     if relation.id is None:
        #         relation.id = str(uuid.uuid4())
        #
        # # 将RelationModel对象转换为字典格式存储
        # self.relation_dict = {
        #     relation.id: relation.dict()  # 使用.dict()将Pydantic模型转为字典
        #     for relation in relations
        #     # if relation.id is not None  # 确保id不为None
        # }

    '''
           实体属性融合
    '''

    def merge_and_filter_es_entities(self, es_hits: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        合并ES实体并只返回存在属性变更的实体
        修改版：属性值用逗号拼接，而不是嵌套数组
        返回格式保持与ES一致
        """
        # 存储结构
        name_groups = defaultdict(list)  # 按name分组原始实体
        changed_entities = []  # 只保留有变更的实体

        # 按name分组
        for hit in es_hits:
            name = hit["_source"]["name"]
            name_groups[name].append(hit)

        # 处理每个name组
        for name, entities in name_groups.items():
            if len(entities) == 1:
                continue  # 单独实体不处理

            # 收集所有属性键（排除source）
            all_keys = set()
            for ent in entities:
                all_keys.update(k for k in ent["_source"]["properties"].keys() if k != "source")

            # 检查每个属性是否需要合并
            props_to_merge = {}
            for key in all_keys:
                values = set()
                for ent in entities:
                    if key in ent["_source"]["properties"]:
                        val = ent["_source"]["properties"][key]
                        # 处理已经是逗号分隔的情况
                        if isinstance(val, str) and "," in val:
                            values.update(v.strip() for v in val.split(","))
                        else:
                            values.add(str(val))

                if len(values) > 1:  # 该属性需要合并
                    props_to_merge[key] = ", ".join(sorted(values))

            # 如果有属性需要合并
            if props_to_merge:
                # 构建合并后的属性（保留原始source）
                for ent in entities:
                    original_props = ent["_source"]["properties"]
                    new_props = original_props.copy()

                    # 只更新需要合并的字段
                    for k, v in props_to_merge.items():
                        # 如果原值已经是逗号分隔，先拆分比较
                        original_val = original_props.get(k, "")
                        if isinstance(original_val, str) and "," in original_val:
                            original_set = set(v.strip() for v in original_val.split(","))
                            merged_set = set(v.strip() for v in v.split(","))
                            if original_set != merged_set:
                                new_props[k] = v
                        elif str(original_val) != v:
                            new_props[k] = v

                    # 只有实际发生变更才加入结果
                    if new_props != original_props:
                        new_props["_merged"] = True
                        changed_entities.append({
                            **{k: v for k, v in ent.items() if k != "_source"},
                            "_source": {
                                **ent["_source"],
                                "properties": new_props
                            }
                        })

        return changed_entities

    '''
            实体关系融合
    '''

    def merge_relations(self,data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        合并相同head和tail的关系，relation用逗号拼接
        只返回产生了合并的关系
        """
        # 使用(head, tail)作为键来分组
        relation_groups = defaultdict(list)

        # 第一次遍历：分组
        for item in data:
            key = (item["head"], item["tail"])
            relation_groups[key].append(item)

        # 第二次遍历：合并
        merged_results = []
        for (head, tail), items in relation_groups.items():
            if len(items) == 1:
                continue  # 没有需要合并的

            # 收集所有不同的relation
            relations = set()
            sources = set()
            for item in items:
                relations.add(item["relation"])
                sources.add(item["source"])

            # 只有当relation不同时才合并
            if len(relations) > 1:
                # 对每个要合并的项创建新版本
                for item in items:
                    merged_item = item.copy()
                    merged_item["relation"] = ", ".join(sorted(relations))
                    merged_item["source"] = ", ".join(sorted(sources))
                    merged_item["_merged"] = True  # 标记为已合并
                    merged_results.append(merged_item)

        return merged_results


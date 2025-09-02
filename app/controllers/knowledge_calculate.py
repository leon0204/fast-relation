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


class KnowledgeCalculateController:
    """知识计算类"""

    def __init__(self, entities: EntityModelListData, relations: List[RelationModel], model_id):
        """
        初始化知识推理器
        :param entities: EntityModelListData 对象
        :param relations: RelationModel 列表
        """
        self.entities_data = entities  # 保存原始数据对象
        self.model_id = model_id  # 保存原始数据对象
        self.relations_data = relations  # 保存原始关系列表


        # 将EntityModel对象转换为字典格式存储
        self.entity_dict = {
            entity.id: entity.dict()  # 使用.dict()将Pydantic模型转为字典
            for entity in entities.data
            if entity.id is not None  # 确保id不为None
        }

        for relation in relations:
            if relation.id is None:
                relation.id = str(uuid.uuid4())

        # 将RelationModel对象转换为字典格式存储
        self.relation_dict = {
            relation.id: relation.dict()  # 使用.dict()将Pydantic模型转为字典
            for relation in relations
            # if relation.id is not None  # 确保id不为None
        }

    '''
    知识推理
    '''
    def apply_reasoning_rules(self) -> Dict[str, Any]:
        """
        应用所有推理规则
        :return: 包含更新后实体和关系的字典
        """
        # 1. 应用实体属性推理规则
        updated_entities = self._apply_entity_reasoning_rules()

        # 2. 应用关系属性推理规则

        updated_relations = self._apply_relation_reasoning_rules()

        # 3. 发现新关系
        new_relations = self._discover_new_relations()



        return {
            "entities": updated_entities,
            "updated_relations": updated_relations,
            "new_relations": new_relations
        }

    def _apply_entity_reasoning_rules(self) -> List[Dict[str, Any]]:
        """
        应用实体属性推理规则
        :return: 更新后的实体列表(字典格式)
        """
        updated_entities = []

        for entity_id, entity_dict in self.entity_dict.items():
            # 创建实体副本以避免修改原始数据
            updated_entity = entity_dict.copy()
            properties = updated_entity.get('properties', {})

            # 规则1: 如果名字包含"毛"，推断可能是政治人物
            if '毛' in entity_dict['name']:
                properties['political_figure'] = True
                properties['possible_era'] = '现代' if '泽' in entity_dict['name'] else '近代'

            # 规则2: 如果名字是"蔡英文"，添加特定属性
            if entity_dict['name'] == '蔡英文':
                properties['current_politician'] = True
                properties['region'] = '台湾'

            # 规则3: 如果名字包含"陈"，推断可能是台湾人物
            if '陈' in entity_dict['name']:
                properties['possible_region'] = '台湾'

            # 规则4: 如果名字是"毛泽东"，添加特定属性
            if entity_dict['name'] == '毛泽东':
                properties['historical_figure'] = True
                properties['possible_era'] = '现代'
                properties['significant_role'] = '国家领导人'

            # 规则5: 如果名字是"毛泽民"，添加与毛泽东的关系属性
            if entity_dict['name'] == '毛泽民':
                properties['related_to'] = '毛泽东'
                properties['family_relation'] = '兄弟'

            updated_entity['properties'] = properties
            updated_entities.append(updated_entity)

        return updated_entities

    def _apply_relation_reasoning_rules(self) -> List[Dict[str, Any]]:
        """
        应用关系属性推理规则
        :return: 更新后的关系列表(字典格式)
        """
        updated_relations = []

        for relation_id, relation_dict in self.relation_dict.items():
            if relation_dict.get('model_id') != self.model_id:
                # 只处理当前模型的关系
                updated_relations.append(relation_dict)
                continue

            updated_relation = relation_dict.copy()
            properties = updated_relation.get('properties', {})

            # 规则1: 如果是"父子"关系，添加家族属性
            if relation_dict['type'] == '父子':
                properties['family_relation'] = True
                properties['generation_gap'] = True

            # 规则2: 如果是"朋友关系"，添加社交属性
            if '朋友' in relation_dict['type']:
                properties['social_connection'] = True
                if '22' in str(properties.values()):
                    properties['strong_connection'] = True

            updated_relation['properties'] = properties
            if properties:
                updated_relations.append(updated_relation)

        return updated_relations

    def _discover_new_relations(self) -> List[Dict[str, Any]]:
        """
        发现新关系
        :return: 新发现的关系列表(字典格式)
        """
        new_relations = []
        model_id = self.model_id

        # 规则1: 发现同姓关系
        name_groups = {}
        for entity in self.entity_dict.values():
            if entity.get('model_id') != model_id:
                continue
            last_name = entity['name'][0]  # 简单取第一个字符作为姓氏
            if last_name not in name_groups:
                name_groups[last_name] = []
            name_groups[last_name].append(entity['id'])

        # 为同姓实体创建"同姓"关系
        for last_name, ids in name_groups.items():
            if len(ids) >= 2:
                for i in range(len(ids)):
                    for j in range(i + 1, len(ids)):
                        source_id = ids[i]
                        target_id = ids[j]

                        # 检查是否已存在相同关系
                        existing_relation = any(
                            r.get('source_id') == source_id and r.get('target_id') == target_id and r.get(
                                'type') == '同姓'
                            for r in self.relation_dict.values()
                        )

                        if not existing_relation:
                            new_relation = {
                                "id": str(uuid.uuid4()),
                                "source_id": source_id,
                                "target_id": target_id,
                                "type": "同姓",
                                "properties": {
                                    "last_name": last_name,
                                    "reason": "相同姓氏"
                                },
                                "model_id": model_id
                            }
                            new_relations.append(new_relation)

        # 规则2: 发现兄弟关系及其传递性
        # 首先收集所有已有的兄弟关系
        existing_brother_relations = {
            (r['source_id'], r['target_id'])
            for r in self.relation_dict.values()
            if r.get('model_id') == model_id and r.get('type') == '兄弟'
        }
        print("relation_dict is ",self.relation_dict)
        print("entities_with_brothers is ",existing_brother_relations)


        # 创建一个字典来存储每个实体的兄弟
        brother_connections = {}
        for source_id, target_id in existing_brother_relations:
            if source_id not in brother_connections:
                brother_connections[source_id] = set()
            if target_id not in brother_connections:
                brother_connections[target_id] = set()
            brother_connections[source_id].add(target_id)
            brother_connections[target_id].add(source_id)

        # 获取所有有兄弟的实体
        entities_with_brothers = set(brother_connections.keys())

        # 对于每对有兄弟的实体，检查是否有共同兄弟
        entities_list = list(entities_with_brothers)
        for i in range(len(entities_list)):
            entity_a = entities_list[i]
            brothers_of_a = brother_connections.get(entity_a, set())

            for j in range(i + 1, len(entities_list)):
                entity_b = entities_list[j]
                brothers_of_b = brother_connections.get(entity_b, set())

                # 如果A和B有共同的兄弟
                if brothers_of_a & brothers_of_b:
                    # 如果A和B之间还没有兄弟关系
                    if (entity_a, entity_b) not in existing_brother_relations and (
                    entity_b, entity_a) not in existing_brother_relations:
                        # 检查是否已经作为新关系添加
                        existing_as_new = any(
                            r.get('source_id') == entity_a and r.get('target_id') == entity_b and r.get('type') == '兄弟'
                            for r in new_relations
                        )

                        if not existing_as_new:
                            # 添加A和B之间的兄弟关系，使用UUID作为ID
                            relation_id = str(uuid.uuid4())

                            new_relation = {
                                "id": relation_id,
                                "source_id": entity_a,
                                "target_id": entity_b,
                                "type": "兄弟",
                                "properties": {
                                    "reason": "通过共同兄弟推断"
                                },
                                "model_id": model_id
                            }
                            new_relations.append(new_relation)

        # 处理兄弟关系的传递性 (使用连通分量方法)
        # 获取所有兄弟关系对
        brother_pairs = list(existing_brother_relations)

        # 创建一个图结构来表示兄弟关系
        from collections import defaultdict
        brother_graph = defaultdict(set)
        for source_id, target_id in brother_pairs:
            brother_graph[source_id].add(target_id)
            brother_graph[target_id].add(source_id)

        # 对于图中的每个连通分量，其中的所有实体都应该两两之间有兄弟关系
        visited = set()
        for entity_id in entities_with_brothers:
            if entity_id not in visited:
                # 开始一个新的连通分量
                component = set()
                stack = [entity_id]
                while stack:
                    current = stack.pop()
                    if current not in visited:
                        visited.add(current)
                        component.add(current)
                        # 添加所有未访问的邻居
                        for neighbor in brother_graph.get(current, set()):
                            if neighbor not in visited:
                                stack.append(neighbor)

                # 在这个连通分量中，所有实体两两之间都应该有兄弟关系
                component_list = list(component)
                for i in range(len(component_list)):
                    for j in range(i + 1, len(component_list)):
                        a = component_list[i]
                        b = component_list[j]
                        # 检查是否已经存在这个关系
                        if (a, b) not in existing_brother_relations and (b, a) not in existing_brother_relations:
                            # 检查是否已经作为新关系添加
                            existing_as_new = any(
                                r.get('source_id') == a and r.get('target_id') == b and r.get('type') == '兄弟'
                                for r in new_relations
                            )

                            if not existing_as_new:
                                # 添加这个关系，使用UUID作为ID
                                relation_id = str(uuid.uuid4())

                                new_relation = {
                                    "id": relation_id,
                                    "source_id": a,
                                    "target_id": b,
                                    "type": "兄弟",
                                    "properties": {
                                        "reason": "通过兄弟关系传递性推断"
                                    },
                                    "model_id": model_id
                                }
                                new_relations.append(new_relation)

        return new_relations

    def get_results(self) -> Dict[str, Any]:
        """
        获取推理结果
        :return: 包含更新后实体和关系的字典
        """
        return self.apply_reasoning_rules()

        # 关系类型情感映射表

    '''
    知识统计
    '''

    def basic_statistics(self) -> Dict:
        """基础统计信息"""
        return {
            "实体总数": self.entities_data.total,
            "关系总数": len(self.relations_data),
            "实体类型分布": defaultdict(int),
            "关系类型分布": defaultdict(int)
        }

    def calculate_statistics(self) -> Dict:
        """计算完整统计信息"""
        stats = self.basic_statistics()

        # 实体类型分布
        for entity in self.entities_data.data:
            stats["实体类型分布"][entity.type] += 1

        # 关系类型分布
        for relation in self.relations_data:
            stats["关系类型分布"][relation.type] += 1

        # 转换defaultdict为普通dict
        stats["实体类型分布"] = dict(stats["实体类型分布"])
        stats["关系类型分布"] = dict(stats["关系类型分布"])

        return stats

    def top_entities_by_property(self, property_name: str, top_n: int = 5) -> List[Dict]:
        """按属性值排序的实体排名"""
        property_entities = []

        for entity in self.entities_data.data:
            if property_name in entity.properties:
                property_entities.append({
                    "id": entity.id,
                    "name": entity.name,
                    "value": entity.properties[property_name]
                })

        # 按属性值降序排序
        sorted_entities = sorted(property_entities, key=lambda x: x["value"], reverse=True)

        return sorted_entities[:top_n]

    '''
    nlp
    '''




    '''
           实体属性融合
    '''


    def merge_entities(self) -> EntityModelListData:
        """
        合并同名实体的properties，只返回属性有新增或变更的实体
        规则：
        1. source字段保持原值不合并
        2. 只返回那些有属性新增(key增加)或变更(value变化)的实体
        3. 完全未变化的实体不返回
        """
        # 存储结构
        original_props = {}  # 记录每个实体原始properties（不含source）
        merged_props = defaultdict(dict)  # 合并后的属性（不含source）
        source_values = {}  # 记录每个实体的原始source

        # 第一次遍历：收集原始数据和合并属性
        for entity in self.entities_data.data:
            entity_id = entity.id
            # 保存原始properties（不含source）
            original_props[entity_id] = {k: v for k, v in entity.properties.items() if k != "source"}
            # 保存原始source
            if "source" in entity.properties:
                source_values[entity_id] = entity.properties["source"]

            # 合并属性（不含source）
            for k, v in entity.properties.items():
                if k == "source":
                    continue
                if k in merged_props[entity.name]:
                    existing = merged_props[entity.name][k]
                    if isinstance(existing, list):
                        if v not in existing:
                            existing.append(v)
                    elif existing != v:
                        merged_props[entity.name][k] = [existing, v]
                else:
                    merged_props[entity.name][k] = v

        # 第二阶段：筛选有变化的实体
        changed_entities = []
        for entity in self.entities_data.data:
            name = entity.name
            entity_id = entity.id

            # 检查是否有属性变化
            has_changes = False
            current_merged = merged_props[name]

            # 情况1：有新key增加
            if any(k not in original_props[entity_id] for k in current_merged):
                has_changes = True
            # 情况2：有value变化
            elif any(
                    (k in original_props[entity_id]) and
                    (original_props[entity_id][k] != current_merged[k])
                    for k in current_merged
            ):
                has_changes = True

            if has_changes:
                # 构建合并后的properties
                final_props = deepcopy(current_merged)
                # 恢复原始source
                if entity_id in source_values:
                    final_props["source"] = source_values[entity_id]
                elif source_values.get(name, {}):
                    # 如果没有source，使用同名实体的第一个source
                    first_source = next(iter(source_values[name].values()))
                    final_props["source"] = first_source

                changed_entities.append(EntityModel(
                    id=entity_id,
                    name=name,
                    type=entity.type,
                    email=entity.email,
                    properties=final_props,
                    model_id=entity.model_id
                ))

        return EntityModelListData(
            total=len(changed_entities),
            data=changed_entities
        )

    '''
               实体关系融合
    '''

    def find_and_create_new_relations(self) -> List[RelationModel]:
        """
        根据text相同找到其他关系，创建新的关系组
        规则：
        1. 找出所有text相同的关系组
        2. 对每组中的每个关系，用其他关系的type与自己的source_id/target_id创建新关系
        3. 为每个新关系生成UUID作为id
        4. 只返回新增的关系组
        """
        # 第一步：按text分组
        text_groups = defaultdict(list)
        for rel in self.relations_data:
            if "text" in rel.properties:
                text_groups[rel.properties["text"]].append(rel)

        # 第二步：生成新关系
        new_relations = []
        for text, group in text_groups.items():
            if len(group) <= 1:
                continue  # 不需要处理单个关系

            # 收集所有关系类型
            all_types = {rel.type for rel in group}

            # 为每个关系创建新关系
            for rel in group:
                existing_types = {rel.type}
                # 找到该关系尚未拥有的其他类型
                for other_type in all_types - existing_types:
                    new_relations.append(RelationModel(
                        id=str(uuid.uuid4()),  # 生成UUID
                        source_id=rel.source_id,
                        target_id=rel.target_id,
                        type=other_type,
                        properties={
                            "text": text,
                            "source": "derived",
                            "original_types": [rel.type, other_type]
                        },
                        model_id=rel.model_id
                    ))

        return new_relations


'''
图挖掘
'''
import community.community_louvain as community_louvain


class GraphMiningAlgorithms:
    def __init__(self, entities: List[EntityModel], relations: List[RelationModel]):
        self.entities = {entity.id: entity for entity in entities}
        self.relations = relations
        self.graph = self._build_graph()

    def _build_graph(self) -> nx.Graph:
        """构建NetworkX图"""
        G = nx.Graph()

        # 添加节点
        for entity in self.entities.values():
            G.add_node(entity.id, name=entity.name, **entity.properties)

        # 添加边
        for relation in self.relations:
            G.add_edge(
                relation.source_id,
                relation.target_id,
                type=relation.type,
                **relation.properties
            )

        return G

    def calculate_centrality(self) -> Dict:
        """计算中心性指标"""
        centrality = {
            "degree_centrality": nx.degree_centrality(self.graph),
            "betweenness_centrality": nx.betweenness_centrality(self.graph),
            "closeness_centrality": nx.closeness_centrality(self.graph)
        }
        return centrality

    def detect_communities(self) -> Dict:
        """社区检测"""
        # 使用Louvain算法检测社区
        partition = community_louvain.best_partition(self.graph)

        # 统计社区分布
        community_distribution = defaultdict(int)
        for node, community_id in partition.items():
            community_distribution[community_id] += 1

        return {
            "partition": partition,
            "community_distribution": dict(community_distribution)
        }

    def find_shortest_paths(self, source_id: str, target_id: str) -> List[List[str]]:
        """查找最短路径"""
        try:
            paths = nx.all_shortest_paths(self.graph, source=source_id, target=target_id)
            return [path for path in paths]
        except nx.NetworkXNoPath:
            return []


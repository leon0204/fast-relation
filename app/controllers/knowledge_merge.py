import logging
import uuid

from fuzzywuzzy import fuzz

logger = logging.getLogger(__name__)
from typing import Dict, Optional, List, Tuple, Any
from app.schemas.knowledge_graph import KnowledgeGraphModel, ModelType, \
    KnowledgeGraphUpdateRequest, KnowledgeGraphModelListData, EntityModel, \
    RelationModel, EntityModelListData


class KnowledgeMergeController:
    """知识融合类"""

    def __init__(self):
        logger.info("知识图谱融合初始化完成")
        # 检查关键词
        self.CHECK_WORDS = {
            "name": ["谁", "名字", "人物", "是谁"],
            "relation": ["关系", "联系", "关联"],
            "property": ["属性", "信息", "资料", "详情"]
        }
        self.RELATION_SENTIMENT_MAP = {
            # 正面关系
            "父母": {"sentiment": "positive", "confidence": 0.8, "explanation": "天然的血缘亲情关系"},
            "夫妻": {"sentiment": "positive", "confidence": 0.7, "explanation": "婚姻关系通常视为正面"},
            "师生": {"sentiment": "positive", "confidence": 0.6, "explanation": "教育关系通常正面"},
            "兄弟姐妹": {"sentiment": "positive", "confidence": 0.75, "explanation": "家庭血缘关系"},
            "情侣": {"sentiment": "positive", "confidence": 0.85, "explanation": "恋爱关系视为正面"},
            "祖孙": {"sentiment": "positive", "confidence": 0.8, "explanation": "家庭血缘关系"},
            "好友": {"sentiment": "positive", "confidence": 0.9, "explanation": "友谊关系视为正面"},
            "亲戚": {"sentiment": "positive", "confidence": 0.7, "explanation": "亲属关系"},
            "同门": {"sentiment": "positive", "confidence": 0.65, "explanation": "师承关系视为正面"},
            "上下级": {"sentiment": "neutral", "confidence": 0.5, "explanation": "工作关系中性"},
            "合作": {"sentiment": "positive", "confidence": 0.7, "explanation": "合作关系通常正面"},

            # 负面关系
            "离婚": {"sentiment": "negative", "confidence": 0.9, "explanation": "婚姻破裂视为负面"},
            "前任秘书": {"sentiment": "negative", "confidence": 0.85, "explanation": "政治敏感关系"},
            "对手": {"sentiment": "negative", "confidence": 0.8, "explanation": "竞争关系"},
            "敌人": {"sentiment": "negative", "confidence": 0.95, "explanation": "敌对关系"},

            # 中性关系
            "unknown": {"sentiment": "neutral", "confidence": 0.5, "explanation": "未知关系类型"},
            "认识": {"sentiment": "neutral", "confidence": 0.5, "explanation": "简单认识关系"},
            "同事": {"sentiment": "neutral", "confidence": 0.5, "explanation": "工作关系中性"}
        }

    # 情感分析
    def analyze_relation(self, relation_type: str) -> dict:
        """
        分析指定关系类型的情感
        :param relation_type: 关系类型字符串
        :return: 情感分析结果字典
        """
        # 标准化关系类型字符串(去除特殊字符)
        normalized_type = relation_type.replace("`", "").strip()

        # 查找预定义的关系情感映射
        if normalized_type in self.RELATION_SENTIMENT_MAP:
            return self.RELATION_SENTIMENT_MAP[normalized_type].copy()

        # 未知关系类型默认处理
        return {
            "sentiment": "neutral",
            "confidence": 0.5,
            "keywords": [normalized_type],
            "explanation": f"未定义的关系类型，默认中性: {normalized_type}"
        }

    # 本体对齐
    def remove_duplicate_entities(self, input_name, input_id, entities, similarity_threshold=80):

        """
            将输入字符串与EntityModelListData中的实体进行比较

            参数:
                input_name: 输入的查询字符串
                entity_list_data: EntityModelListData实例
                similarity_threshold: 相似度阈值(0-100)

            返回:
                包含比较结果的字典
            """
        # 从Pydantic模型中提取原始数据
        entities: List[EntityModel] = entities.data

        # ======================
        # 1. 数据预处理 - 去除重复实体
        # ======================
        unique_entities: List[EntityModel] = []
        removed_entities: List[Dict[str, Any]] = []  # 记录被移除的实体

        for entity in entities:
            name = entity.name
            if name == input_name and input_id != entity.id:
                # 重复出现，记录移除
                removed_entities.append({
                    "id": entity.id,
                    "properties": entity.properties,
                    "name": name,
                    "reason": "duplicate",
                    "type": "duplicate"
                })
            else:
                unique_entities.append(entity)

        # ======================
        # 2. 本体对齐 - 基于字符串相似度
        # ======================
        # 2.1 查找完全匹配的实体
        # 预定义已知别名映射(可根据需要扩展)
        known_aliases = {
            "鲁迅": ["周树人"],
            "周树人": ["鲁迅"],
            # 可以添加更多已知别名
        }

        # exact_matches = [entity for entity in unique_entities if entity.name == input_name]

        # 2.2 查找相似名称的实体并标记为需要移除
        # similar_entities_info: List[Dict[str, Any]] = []  # 仅用于记录相似信息
        removed_entities_from_similarity: List[Dict[str, Any]] = []  # 因相似度过高而需要移除的实体

        for entity in unique_entities:
            s_type = "similarity"
            name = entity.name  # 使用点号访问属性
            if name != input_name:  # 跳过完全匹配的情况
                # 先检查是否是已知别名
                if input_name in known_aliases and name in known_aliases[input_name]:
                    similarity = 100  # 已知别名视为完全匹配 alias
                    s_type = "alias"
                else:
                    # 否则计算常规相似度
                    similarity = fuzz.ratio(input_name, name)
                if similarity >= similarity_threshold:
                    # similar_entities_info.append({
                    #     "entity_id": entity.id,
                    #     "entity_name": name,
                    #     "similarity": similarity
                    # })
                    # 将相似实体添加到移除列表
                    removed_entities_from_similarity.append({
                        "id": entity.id,
                        "name": name,
                        "properties": entity.properties,
                        "reason": f"similarity_to_{input_name}_({similarity})",
                        "type": s_type
                    })

        # 合并原始移除列表和因相似度过高而移除的实体
        removed_entities.extend(removed_entities_from_similarity)

        # ======================
        # 3. 返回综合结果
        # ======================
        return {
            "input_name": input_name,

            # "similar_entities_info": similar_entities_info,
            "removed_entities": removed_entities,
            "unique_entities_count": len(unique_entities),
            "removed_count": len(removed_entities)
        }

    def format_name_query_result(self, result: dict) -> dict:
        """
        格式化名称查询结果为自然语言回复
        """
        if not result or len(result) == 0:
            return {"answer": "对不起，未能理解您的问题～", "details": []}

        entities = result
        answers = []

        for entity in entities:
            # 基础信息
            answer = f"找到人物：{entity['name']}"

            # 添加额外信息（如果有）
            if entity.get("email"):
                answer += f"，邮箱：{entity['email']}"
            if entity.get("type"):
                answer += f"，类型：{entity['type']}"
            if entity.get("model_id"):
                answer += f"，所属模型：{entity['model_id']}"

            # 如果有额外属性
            if entity.get("properties") and len(entity["properties"]) > 0:
                properties_str = ", ".join([f"{k}: {v}" for k, v in entity["properties"].items()
                                            if k not in ["id", "name", "email", "type"]])
                if properties_str:
                    answer += f"，附加属性：{properties_str}"

            answers.append(answer)

        # 根据找到的人物数量组织回答
        if len(answers) == 1:
            final_answer = answers[0] + "。"
        else:
            names = [entity["name"] for entity in entities]
            final_answer = f"找到{len(names)}个人物：{', '.join(names)}。"

        return {
            "answer": final_answer,
            "details": result
        }

    def format_relation_query_result(self, result: dict) -> dict:
        """
        格式化关系查询结果为自然语言回复
        """
        print("result 2", result)

        if not result or len(result) == 0:
            return {"answer": "没有找到相关人物之间的关系", "details": []}

        relations = result
        answers = []

        props = ""
        for relation in relations:
            # 基础关系信息
            answer = f"{relation['source_name']} 和 {relation['target_name']} 之间存在 {relation['relation_type']} 关系"
            # 添加关系属性（如果有）
            if relation['relation_properties'] and len(relation['relation_properties']) > 0:
                for k, v in relation['relation_properties'].items():
                    if k != "id" and k != "type":
                        if k == "text":
                            k = "为您找到以下资料："
                        props += "\n" + k + v
                # answer += f"，关系属性：{props}"
                answer += props

            # 添加模型信息
            if relation.get('model_id'):
                answer += f"，所属模型：{relation['model_id']}"

            answers.append(answer)

        # 根据找到的关系数量组织回答
        if len(answers) == 1:
            final_answer = answers[0] + "。"
        else:
            pairs = [f"{r['source_name']}与{r['target_name']}" for r in relations]
            final_answer = f"找到{len(relations)}组人物关系：{', '.join(pairs)}。"
        final_answer = "为您找到人物关系：" + final_answer
        return {
            "answer": final_answer,
            "details": result
        }

    def format_properties(self,properties):
        # 定义字段映射（字段名: 中文显示名）
        field_map = {
            'age': '年龄',
            'birth_year': '出生年份',
            'occupation': '职业',
            'address': '住址',
            'hobby': '爱好',
            'identity': '身份',
            'role': '角色',
            'text': '相关资料'
        }

        # 提取有效属性
        valid_props = []
        for field, display_name in field_map.items():
            if field in properties:
                value = str(properties[field])  # 强制转为字符串
                valid_props.append(display_name + "：" + value)

        # 拼接最终字符串
        name = properties.get('name', '')
        if valid_props:
            return name + "，" + "，".join(valid_props) + "。"
        else:
            return name + "（暂无详细信息）"

    def format_property_query_result(self, result: dict) -> dict:
        """
        格式化属性查询结果为自然语言回复
        """

        if not result or len(result) == 0:
            return {"answer": "没有找到该人物的属性信息", "details": []}

        properties_list = result
        answers = []

        for prop in properties_list:
            # 基础信息
            answer = f"{prop['name']}的属性信息："


            # 添加属性详情
            if prop.get("properties") and len(prop["properties"]) > 0:
                # 替换
                props  = self.format_properties(prop["properties"])
                print("props si",props)
                # props = "\n".join([f"- {k}: {v}" for k, v in prop["properties"].items()])
                answer += str(props) +"\n"
            else:
                answer += " 没有额外的属性信息"


            # 添加模型信息
            # if prop.get('model_id'):
            #     answer += f"，所属模型：{prop['model_id']}"

            answers.append(answer)

        print("answers is ",answers)

        # 根据找到的人物数量组织回答
        if len(answers) == 1:
            final_answer = answers[0]
        else:
            # details = "\n\n".join(answers)
            # final_answer = f"多个匹配人物的属性信息：\n\n{details}"
            final_answer = max(answers, key=lambda x: len(x))

        return {
            "answer": final_answer,
            "details": result
        }

    def detect_query_type(self, question: str) -> str:
        """检测查询类型"""

        question_lower = question.lower()
        for q_type, keywords in self.CHECK_WORDS.items():
            if any(keyword in question_lower for keyword in keywords):
                return q_type
        return "name"  # 默认按名称查询

    def format_query_result(self, query_type: str, result: dict) -> dict:
        """
        根据查询类型格式化查询结果为自然语言回复
        """
        if query_type == "name":
            return self.format_name_query_result(result)
        elif query_type == "relation":
            return self.format_relation_query_result(result)
        elif query_type == "property":
            return self.format_property_query_result(result)
        else:
            return {"answer": "无法理解的查询类型", "details": {}}


knowledgeMergeController = KnowledgeMergeController()

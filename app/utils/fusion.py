"""
fusion
实现实体属性融合：
1. 调用标准化规则
2. 冲突解决策略：取最新 update_time 的属性值
"""

from collections import defaultdict
import yaml
import os

import re
from datetime import datetime


def normalize_date(date_str: str) -> str:
    """
    将多种日期格式统一成 'YYYY-MM-DD' 格式。
    例如 "1990年1月1日" -> "1990-01-01"
    """
    if not date_str:
        return ""

    date_str = date_str.strip()
    try:
        # 替换中文年月日为“-”
        date_str = date_str.replace("年", "-").replace("月", "-").replace("日", "")
        # 解析成日期对象
        dt = datetime.strptime(date_str, "%Y-%m-%d")
        return dt.strftime("%Y-%m-%d")
    except Exception:
        # 如果解析失败，直接返回原字符串
        return date_str


def normalize_gender(gender_str: str) -> str:
    """
    性别标准化，将多种表达归一到 Male、Female 或 Unknown。
    """
    if not gender_str:
        return "Unknown"

    gender_str = gender_str.strip().lower()
    if gender_str in ["男", "male", "m", "man", "男性"]:
        return "Male"
    if gender_str in ["女", "female", "f", "woman", "女性"]:
        return "Female"
    return "Unknown"


def normalize_education(edu_str: str) -> str:
    """
    学历标准化，将多种学历表达映射到统一词，如 PhD, Master, Bachelor 等。
    """
    if not edu_str:
        return "Other"

    edu_str = edu_str.strip().lower()
    mapping = {
        "博士": "PhD",
        "phd": "PhD",
        "博士研究生": "PhD",
        "硕士": "Master",
        "master": "Master",
        "硕士研究生": "Master",
        "本科": "Bachelor",
        "学士": "Bachelor",
        "bachelor": "Bachelor",
        "大专": "Associate",
        "中专": "High School",
        "高中": "High School"
    }
    for key, val in mapping.items():
        if key in edu_str:
            return val
    return "Other"


def normalize_location(loc_str: str) -> str:
    """
    地点字段清洗，去除空格，替换中文逗号为英文逗号。
    """
    if not loc_str:
        return ""

    loc_str = loc_str.strip()
    loc_str = loc_str.replace(" ", "").replace("，", ",")
    return loc_str


def normalize_name(name_str: str) -> str:
    """
    人名标准化，去除多余空格，首字母大写。
    """
    if not name_str:
        return ""

    return name_str.strip().title()


def normalize_id(id_str: str) -> str:
    """
    清洗身份证、工号等字段，仅保留字母和数字。
    """
    if not id_str:
        return ""

    return re.sub(r"[^\w]", "", id_str.strip())


def standardize_attributes(entity):
    """
    对实体属性进行标准化处理
    """
    if "birth_date" in entity:
        entity["birth_date"] = normalize_date(entity["birth_date"])
    if "gender" in entity:
        entity["gender"] = normalize_gender(entity["gender"])
    if "education" in entity:
        entity["education"] = normalize_education(entity["education"])
    if "location" in entity:
        entity["location"] = normalize_location(entity["location"])
    if "name" in entity:
        entity["name"] = normalize_name(entity["name"])
    if "id" in entity:
        entity["id"] = normalize_id(entity["id"])
    return entity


def fuse_entities(entity_list):
    """
    实体属性融合，按 id 聚合，
    同一属性冲突时，取 update_time 最新的值。
    """
    fused = {}

    # 用于记录每个实体每个属性最新时间和对应值
    latest_attr = defaultdict(lambda: defaultdict(lambda: {"time": None, "value": None}))

    for entity in entity_list:
        entity_id = entity.get("id")
        if not entity_id:
            continue
        # 标准化
        std_entity = standardize_attributes(entity)
        update_time_str = std_entity.get("update_time")
        try:
            update_time = datetime.fromisoformat(update_time_str) if update_time_str else None
        except Exception:
            update_time = None

        if entity_id not in fused:
            fused[entity_id] = {}

        for key, val in std_entity.items():
            if key == "id" or key == "update_time":
                continue

            last_record = latest_attr[entity_id][key]
            if last_record["time"] is None or (update_time and update_time > last_record["time"]):
                latest_attr[entity_id][key] = {"time": update_time, "value": val}
                fused[entity_id][key] = val

    # 添加 id 到融合结果
    for eid in fused:
        fused[eid]["id"] = eid

    # 转换为列表返回
    return list(fused.values())


def resolve_relation_conflict(relations: list[dict]) -> dict:
    """
    解决同一实体对的多关系冲突
    :param relations:
    :return: 融合后的关系列表
    """
    # 按可信度规则排序 (示例规则：1. 时间最新 2. 指定数据源优先)
    sorted_rels = sorted(
        relations,
        key=lambda x: (
            -datetime.strptime(x["timestamp"], "%Y-%m-%d").timestamp(),
            x["source"] != "权威数据源"  # 假设有个可信数据源标记
        )
    )

    # 保留所有关系但标记主要关系
    return {
        "primary_relation": sorted_rels[0]["relation"],
        "all_relations": relations
    }


here = os.path.dirname(os.path.abspath(__file__))

relation_mapping_path  = os.path.join(here, '../datasets/relation_mapping.yaml')
with open(relation_mapping_path, "r", encoding="utf-8") as f:
    mapping = yaml.safe_load(f)


def map_relation(cn_relation):
    for key, info in mapping.items():
        if cn_relation == key or cn_relation in info.get("alias", []):
            return info.get("standard")
    return cn_relation

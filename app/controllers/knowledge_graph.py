import json
import math
import re
import uuid
from datetime import datetime
import hashlib
import logging
import threading
from typing import Dict, Optional, List, Tuple, Any

from fastapi import HTTPException

from app.utils.database import get_neo4j_db_sync
from app.schemas.knowledge_graph import KnowledgeGraphModel, ModelType, \
    KnowledgeGraphUpdateRequest, KnowledgeGraphModelListData, EntityModel, \
    RelationModel, EntityModelListData, DefaultName
import jieba

logger = logging.getLogger(__name__)


class Neo4jController:
    """Neo4j数据库连接管理类"""

    def __init__(self):
        self.driver = get_neo4j_db_sync()
        # self._initialize_schema()

    def _initialize_schema(self):
        """初始化数据库索引和约束"""
        with self.driver.session() as session:
            # 创建索引（加速查询）
            session.run("CREATE INDEX FOR (e:EntitySearch) ON (e.name)")
            session.run("CREATE INDEX FOR (c:Concept) ON (c.name)")
            session.run("CREATE INDEX FOR (d:Document) ON (d.title)")
            session.run("CREATE INDEX FOR (p:Person) ON (p.name)")
            session.run("CREATE INDEX FOR (e:Event) ON (e.name)")

    def execute_query(self, query: str, params: Optional[Dict] = None):
        """执行数据库查询"""
        try:
            with self.driver.session() as session:
                result = session.run(query, params or {})
                return [record.data() for record in result]
        except Exception as e:
            logger.error(f"执行查询失败: {str(e)}")
            raise e


class KnowledgeGraphController:
    """知识图谱核心管理类，处理模型、实体、关系的全生命周期管理"""

    def __init__(self, db: Neo4jController):
        """初始化知识图谱管理器"""
        self.db = db
        self.lock = threading.Lock()  # 用于并发控制的锁
        self.models = {}  # 存储加载的模型
        # self._initialize_nlp()  # 初始化NLP组件
        self.initialize_schema()  # 初始化数据库模式
        self.load_models()  # 加载已有模型
        logger.info("知识图谱管理器初始化完成")

    # def _initialize_nlp(self):
    #     """初始化自然语言处理组件"""
    #     try:
    #         from transformers import pipeline
    #         # 由于模型加载较慢，使用延迟加载
    #         self.ner_pipeline = None
    #         self.nlp = None
    #         self.vectorizer = None
    #     except Exception as e:
    #         logger.error(f"NLP组件初始化失败: {str(e)}")

    def initialize_schema(self):
        """初始化数据库模式，创建必要的索引和约束"""
        logger.info("开始初始化数据库模式...")
        queries = [
            "CREATE CONSTRAINT IF NOT EXISTS FOR (m:Model) REQUIRE m.id IS UNIQUE",
            "CREATE CONSTRAINT IF NOT EXISTS FOR (e:EntityModel) REQUIRE e.id IS UNIQUE",
            "CREATE CONSTRAINT IF NOT EXISTS FOR (r:RelationModel) REQUIRE r.id IS UNIQUE",
            # "CREATE CONSTRAINT IF NOT EXISTS FOR (d:Document) REQUIRE d.id IS UNIQUE",
            "CREATE INDEX IF NOT EXISTS FOR (m:Model) ON (m.name)",
            "CREATE INDEX IF NOT EXISTS FOR (e:EntityModel) ON (e.name)",
            "CREATE INDEX IF NOT EXISTS FOR (e:EntityModel) ON (e.type)",
            "CREATE INDEX IF NOT EXISTS FOR (r:RelationModel) ON (r.type)"
        ]
        for query in queries:
            try:
                self.db.execute_query(query)
            except Exception as e:
                logger.warning(f"执行模式初始化查询失败: {str(e)}")
        logger.info("数据库模式初始化完成")

    def load_models(self):
        """从数据库加载所有模型到内存"""
        logger.info("开始加载知识图谱模型...")
        query = "MATCH (m:Model) RETURN m"
        try:
            results = self.db.execute_query(query)
            for result in results:
                model_data = result['m']
                model = KnowledgeGraphModel(**model_data)
                self.models[model.id] = model
            logger.info(f"成功加载 {len(self.models)} 个知识图谱模型")
        except Exception as e:
            logger.error(f"加载模型失败: {str(e)}")

    def create_model(self, model: KnowledgeGraphModel) -> KnowledgeGraphModel:
        """创建新的知识图谱模型"""
        logger.info(f"创建知识图谱模型: {model.name}")
        with self.lock:
            # 生成模型ID
            if not model.id:
                model.id = hashlib.sha256(f"{model.name}_{datetime.now()}".encode()).hexdigest()[:16]

            model.created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            model.updated_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            # 保存模型到数据库
            query = """
            MERGE (m:Model {id: $id})
            ON CREATE SET m.name = $name, m.created_by = $created_by, m.description = $description, m.type = $type,
                          m.created_at = $created_at, m.updated_at = $updated_at
            ON MATCH SET m.name = $name, m.created_by = $created_by, m.description = $description, m.type = $type,
                         m.updated_at = $updated_at
            RETURN m
            """

            try:
                self.db.execute_query(query, {
                    "id": model.id,
                    "name": model.name,
                    "created_by": model.created_by,
                    "description": model.description,
                    "type": ModelType.KNOWLEDGE_GRAPH,
                    "created_at": model.created_at,
                    "updated_at": model.updated_at,
                })
            except Exception as e:
                logger.error(f"创建模型失败: {str(e)}")
                raise HTTPException(status_code=500, detail=f"模型创建失败: {str(e)}")

            # 更新内存中的模型
            self.models[model.id] = model
            logger.info(f"知识图谱模型创建成功: {model.id}")
            return model

    def get_model(self, model_id: str) -> KnowledgeGraphModel:
        """获取指定ID的知识图谱模型"""
        if model_id not in self.models:
            logger.warning(f"请求的模型不存在: {model_id}")
            raise HTTPException(status_code=404, detail="模型不存在")

        # 从数据库获取模型
        query = """
        MATCH (m:Model {id: $id})
        RETURN m
        """

        try:
            results = self.db.execute_query(query, {"id": model_id})
            if not results:
                raise HTTPException(status_code=404, detail="模型不存在")

            model_data = results[0]['m']

            # 创建并返回模型对象
            return KnowledgeGraphModel(**model_data)
        except Exception as e:
            logger.error(f"获取模型失败: {str(e)}")
            raise HTTPException(status_code=500, detail=f"获取模型失败: {str(e)}")

    def get_models(self, page: int, page_size: int) -> KnowledgeGraphModelListData:
        """获取所有知识图谱模型"""
        # 判断页码是否超出范围
        if page < 1 or page_size < 1:
            return KnowledgeGraphModelListData(total=0, data=[])

        total = len(self.models)
        start = (page - 1) * page_size
        end = start + page_size
        if start > total:
            return KnowledgeGraphModelListData(total=0, data=[])
        if end > total:
            end = total
        return KnowledgeGraphModelListData(total=total, data=list(self.models.values())[start:end])

    def search_model(self, query: str, time_range: Tuple[datetime, datetime], page: int,
                     page_size: int) -> KnowledgeGraphModelListData:
        """搜索知识图谱模型"""
        # 计算跳过的记录数
        skip = (page - 1) * page_size

        # 查询总记录数
        count_query = """
        MATCH (m:Model)
        WHERE m.name CONTAINS $query
        AND m.created_at >= $start_time AND m.created_at <= $end_time
        RETURN count(m) as total
        """
        parameters = {
            "query": query,
            "start_time": time_range[0].strftime("%Y-%m-%d %H:%M:%S"),
            "end_time": time_range[1].strftime("%Y-%m-%d %H:%M:%S"),
            "skip": skip,
            "limit": page_size
        }
        try:
            results = self.db.execute_query(count_query, parameters)
            total = results[0]['total']
        except Exception as e:
            logger.error(f"获取总记录数失败: {str(e)}")
            raise HTTPException(status_code=500, detail=f"获取总记录数失败: {str(e)}")

        # 查询数据库
        search = """
        MATCH (m:Model)
        WHERE m.name CONTAINS $query
        AND m.created_at >= $start_time AND m.created_at <= $end_time
        RETURN m
        ORDER BY m.created_at DESC
        SKIP $skip
        LIMIT $limit
        """

        try:
            results = self.db.execute_query(search, {
                "query": query,
                "start_time": time_range[0].strftime("%Y-%m-%d %H:%M:%S"),
                "end_time": time_range[1].strftime("%Y-%m-%d %H:%M:%S"),
                "skip": skip,
                "limit": page_size
            })
            if len(results) == 0:
                total = 0

            response = []
            for result in results:
                model_data = result['m']
                response.append(KnowledgeGraphModel(**model_data))
            return KnowledgeGraphModelListData(total=total, data=response)
        except Exception as e:
            logger.error(f"搜索模型失败: {str(e)}")
            raise HTTPException(status_code=500, detail=f"搜索模型失败: {str(e)}")

    def update_model(self, model_id: str, updated_model: KnowledgeGraphUpdateRequest) -> KnowledgeGraphModel:
        """更新知识图谱模型"""
        if model_id not in self.models:
            logger.warning(f"更新失败，模型不存在: {model_id}")
            raise HTTPException(status_code=404, detail="模型不存在")

        existing_model = self.models[model_id]

        # 更新模型属性
        for field, value in updated_model.model_dump(exclude_unset=True).items():
            setattr(existing_model, field, value)

        existing_model.updated_at = datetime.now()

        # 更新数据库
        query = """
        MATCH (m:Model {id: $id})
        SET m.name = $name, m.description = $description, m.updated_at = $updated_at
        RETURN m
        """

        try:
            self.db.execute_query(query, {
                "id": existing_model.id,
                "name": existing_model.name,
                "description": existing_model.description,
                # "type": existing_model.type,
                "updated_at": str(existing_model.updated_at)
            })
        except Exception as e:
            logger.error(f"更新模型失败: {str(e)}")
            raise HTTPException(status_code=500, detail=f"模型更新失败: {str(e)}")

        logger.info(f"知识图谱模型更新成功: {model_id}")
        return existing_model

    def delete_model(self, model_id: str) -> Dict[str, str]:
        """删除知识图谱模型及其所有关联数据"""
        if model_id not in self.models:
            logger.warning(f"删除失败，模型不存在: {model_id}")
            raise HTTPException(status_code=404, detail="模型不存在")

        # 删除模型相关的所有数据
        queries = [
            f"MATCH (m:Model {{id: '{model_id}'}})-[r1]->() DELETE r1",
            f"MATCH ()-[r2]->(m:Model {{id: '{model_id}'}}) DELETE r2",
            f"MATCH (m:Model {{id: '{model_id}'}}) DELETE m",
            f"MATCH (e:Entity {{model_id: '{model_id}'}})-[r3]->() DELETE r3",
            f"MATCH ()-[r4]->(e:Entity {{model_id: '{model_id}'}}) DELETE r4",
            f"MATCH (e:Entity {{model_id: '{model_id}'}}) DELETE e",
        ]

        query = """
        MATCH (m:Model {id: $model_id})
        // 找到该模型下所有的实体
        OPTIONAL MATCH (m)-[:HAS_ENTITY]->(e:Entity)
        // 找到这些实体之间或与外部实体之间的所有关系
        OPTIONAL MATCH (e)-[r]-() // 找到实体 e 的所有出入关系
        
        // 收集所有要删除的实体和关系，避免重复删除和循环依赖
        WITH m, COLLECT(DISTINCT e) AS entities_to_delete, COLLECT(DISTINCT r) AS relations_to_delete
        
        // 删除关系
        FOREACH (rel IN relations_to_delete | DELETE rel)
        // 删除实体 (DETACH DELETE 是为了确保实体上的所有关系都被删除)
        FOREACH (entity IN entities_to_delete | DETACH DELETE entity)
        // 最后删除模型本身 (DETACH DELETE 是为了确保所有 HAS_ENTITY 关系被删除)
        DETACH DELETE m
        """
        parameters = {"model_id": model_id}
        try:
            self.db.execute_query(query, parameters)
        except Exception as e:
            logger.error(f"删除模型关联数据失败: {str(e)}")

        # 从内存中删除模型
        del self.models[model_id]
        logger.info(f"知识图谱模型删除成功: {model_id}")
        return {"status": "success", "message": "模型已删除"}

    def create_entity(self, model_id: str, entity_data: EntityModel) -> EntityModel:
        """
        创建一个新的实体节点。
        """
        entity_id = entity_data.id if entity_data.id else str(uuid.uuid4())
        # entity_data.created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        # entity_data.updated_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        all_properties = {
            "id": entity_id,
            "name": entity_data.name,
            "type": ModelType.ENTITY.value,
            "email": entity_data.email,
        }
        all_properties.update(entity_data.properties)

        query = f"""
        CREATE (e:Entity $props) // 创建实体节点
        WITH e // 将新创建的实体 e 传递到下一个子句

        // 查找模型并创建 HAS_ENTITY 关系
        MATCH (m:Model {{id: $model_id}}) // 使用函数参数 model_id
        CREATE (m)-[r:HAS_ENTITY {{id: $has_entity_rel_id}}]->(e) // ⚠️ 为 HAS_ENTITY 关系添加唯一ID

        RETURN e.id AS id, e.name AS name, e.email AS email, e.type AS type,
        properties(e) AS properties, m.id AS model_id // 返回模型ID
        """
        has_entity_rel_id = str(uuid.uuid4())
        parameters = {
            "props": all_properties,
            "model_id": model_id,
            "has_entity_rel_id": has_entity_rel_id
        }
        results = self.db.execute_query(query, parameters)
        if not results:
            raise HTTPException(status_code=500, detail="实体创建失败")

        result_data = results[0]
        returned_properties = {k: v for k, v in result_data["properties"].items() if
                               k not in ["id", "name", "email", "type"]}
        return EntityModel(
            id=result_data["id"],
            name=result_data["name"],
            email=result_data["email"],
            type=result_data["type"],
            properties=returned_properties,
            model_id=result_data["model_id"],
        )

    def create_bulk_entities(self, model_id: str, entities_data: List[EntityModel]) -> List[EntityModel]:
        return [self.create_entity(model_id, entity_data) for entity_data in entities_data]

    def get_entity(self, entity_id: str) -> EntityModel:
        """
        根据 ID 获取一个实体节点。
        """
        query = """
        MATCH (e:Entity {id: $entity_id})
        OPTIONAL MATCH (m:Model)-[:HAS_ENTITY]->(e)
        RETURN e.id AS id, e.name AS name, e.email AS email, e.type AS type, properties(e) AS properties, m.id AS model_id
        """
        parameters = {"entity_id": entity_id}
        results = self.db.execute_query(query, parameters)
        if not results:
            raise HTTPException(status_code=404, detail="实体不存在")

        result_data = results[0]
        returned_properties = {}
        for k, v in result_data["properties"].items():
            if k not in ["id", "name", "email", "type"]:
                # --- 关键修改：反序列化 'shortest_paths' 属性 ---
                if k == "shortest_paths" and isinstance(v, str):  # 假设 'shortest_paths' 是存储 JSON 的属性名
                    try:
                        returned_properties[k] = json.loads(v)
                    except json.JSONDecodeError:
                        # 如果解析失败，记录警告并保留原始字符串值
                        logging.warning(f"属性 '{k}' 的值不是有效的 JSON 字符串: {v}")
                        returned_properties[k] = v
                else:
                    returned_properties[k] = v
        return EntityModel(
            id=result_data["id"],
            name=result_data["name"],
            email=result_data["email"],
            type=result_data["type"],
            properties=returned_properties,
            model_id=result_data["model_id"],
        )

    def get_entities_by_model(self, model_id: str, page: int, page_size: int) -> EntityModelListData:
        """
        获取指定模型下所有实体节点的列表。
        """
        # 计算 skip 值
        calculated_skip = (page - 1) * page_size
        if calculated_skip < 0:  # 防止 page 小于 1 导致 skip 为负数
            calculated_skip = 0

        # --- 第一步：获取总数 ---
        count_query = """
        MATCH (m:Model {id: $model_id})-[:HAS_ENTITY]->(e:Entity)
        """
        count_parameters = {"model_id": model_id}
        count_query += "RETURN count(e) AS total_count"

        total_count_result = self.db.execute_query(count_query, count_parameters)
        total_count = total_count_result[0]["total_count"] if total_count_result else 0

        # --- 第二步：获取分页数据 ---
        # 基础查询
        query = """
        MATCH (m:Model {id: $model_id})-[:HAS_ENTITY]->(e:Entity)
        """
        parameters = {"model_id": model_id}
        # 应用分页
        query += """
        OPTIONAL MATCH (parent_model:Model)-[:HAS_ENTITY]->(e)
        RETURN e.id AS id, e.name AS name, e.email AS email, e.type AS type, 
        properties(e) AS properties, m.id AS model_id
        SKIP $skip
        LIMIT $limit
        """
        parameters["skip"] = calculated_skip  # 使用计算出的 skip
        parameters["limit"] = page_size  # limit 就是 page_size
        results = self.db.execute_query(query, parameters)

        if len(results) == 0:
            total_count = 0

        entities = []
        for result_data in results:
            returned_properties = {}
            for k, v in result_data["properties"].items():
                if k not in ["id", "name", "email", "type"]:
                    # --- 关键修改：反序列化 'shortest_paths' 属性 ---
                    if k == "shortest_paths" and isinstance(v, str):
                        try:
                            returned_properties[k] = json.loads(v)
                        except json.JSONDecodeError:
                            logging.warning(f"属性 '{k}' 的值不是有效的 JSON 字符串: {v}")
                            returned_properties[k] = v
                    else:
                        returned_properties[k] = v
            entities.append(EntityModel(
                id=result_data["id"],
                name=result_data["name"],
                email=result_data["email"],
                type=result_data["type"],
                properties=returned_properties,
                model_id=result_data["model_id"],
            ))
        return EntityModelListData(total=total_count, data=entities)

    def search_entities(
            self,
            query: str,
            model_id: Optional[str] = None,
            entity_type: Optional[str] = None,
            limit: int = 200
    ) -> List[EntityModel]:
        """
        根据关键词搜索实体。
        可以指定模型ID和实体类型进行筛选。
        """
        base_query = """
                MATCH (e:Entity)
                """
        where_clauses = []
        parameters = {"query_regex": f"(?i).*{query}.*"}  # 不区分大小写的模糊匹配

        # 如果指定了 model_id，则添加关系匹配和WHERE条件
        if model_id:
            base_query += "MATCH (m:Model {id: $model_id})-[:HAS_ENTITY]->(e)\n"
            parameters["model_id"] = model_id

        # 如果指定了 entity_type
        if entity_type:
            where_clauses.append("e.type = $entity_type")
            parameters["entity_type"] = entity_type

        # ⚠️ 关键修改：只搜索 'name' 属性
        search_condition = "e.name =~ $query_regex"
        where_clauses.append(search_condition)

        # 组合所有 WHERE 子句
        if where_clauses:
            base_query += "WHERE " + " AND ".join(where_clauses)

        # 返回语句
        base_query += """
                OPTIONAL MATCH (parent_model:Model)-[:HAS_ENTITY]->(e)
                RETURN e.id AS id, e.name AS name, e.email AS email, e.type AS type, properties(e) AS properties, parent_model.id AS 
                model_id
                LIMIT $limit
                """
        parameters["limit"] = limit

        results = self.db.execute_query(base_query, parameters)

        entities = []
        for result_data in results:
            returned_properties = {}
            for k, v in result_data["properties"].items():
                if k not in ["id", "name", "email", "type"]:
                    # --- 关键修改：反序列化 'shortest_paths' 属性 ---
                    if k == "shortest_paths" and isinstance(v, str):
                        try:
                            returned_properties[k] = json.loads(v)
                        except json.JSONDecodeError:
                            logging.warning(f"属性 '{k}' 的值不是有效的 JSON 字符串: {v}")
                            returned_properties[k] = v
                    else:
                        returned_properties[k] = v

            entities.append(EntityModel(
                id=result_data["id"],
                name=result_data["name"],
                email=result_data["email"],
                type=result_data["type"],
                properties=returned_properties,
                model_id=result_data["model_id"],
            ))
        return entities

    def update_entity(self, entity_id: str, update_data: Dict[str, Any]) -> EntityModel:
        """
        更新实体节点的属性和/或类型。
        """
        current_entity = self.get_entity(entity_id)

        props_to_set = {}
        if 'name' in update_data:
            props_to_set['name'] = update_data['name']
        if 'type' in update_data:
            props_to_set['type'] = update_data['type']
        if 'email' in update_data:
            props_to_set['email'] = update_data['email']

        if 'properties' in update_data:
            updated_dynamic_props = current_entity.properties.copy()
            if updated_dynamic_props.get("shortest_paths") is not None:
                updated_dynamic_props["shortest_paths"] = json.dumps(updated_dynamic_props["shortest_paths"])

            for key, value in update_data['properties'].items():
                # --- 关键修改：序列化特定属性 ---
                if key == "shortest_paths" and isinstance(value, dict):  # 检查是否为 shortest_paths 字典
                    try:
                        updated_dynamic_props[key] = json.dumps(value)  # 序列化为 JSON 字符串
                    except TypeError:
                        logger.error(f"无法将属性 '{key}' 的值序列化为 JSON: {value}")
                        updated_dynamic_props[key] = value  # 序列化失败则保留原值或报错
                else:
                    updated_dynamic_props[key] = value
            props_to_set.update(updated_dynamic_props)

        type_label_update = ""
        if 'type' in update_data and update_data['type'] != current_entity.type:
            type_label_update = f" REMOVE e:{current_entity.type} SET e:{update_data['type']}"

        query = f"""
        MATCH (e:Entity {{id: $entity_id}})
        {type_label_update}
        SET e += $props_to_set
        RETURN e.id AS id, e.name AS name, e.email AS email, e.type AS type, properties(e) AS properties,
               (CASE WHEN EXISTS((:Model)-[:HAS_ENTITY]->(e)) THEN head([(m:Model)-[:HAS_ENTITY]->(e) | m.id]) ELSE null END) AS model_id
        """
        parameters = {"entity_id": entity_id, "props_to_set": props_to_set}

        results = self.db.execute_query(query, parameters)
        if not results:
            raise HTTPException(status_code=500, detail="实体更新失败")

        result_data = results[0]
        returned_properties = {}
        for k, v in result_data["properties"].items():
            if k not in ["id", "name", "email", "type"]:
                # --- 关键修改：反序列化特定属性，与 get_entity 保持一致 ---
                if k == "shortest_paths" and isinstance(v, str):
                    try:
                        returned_properties[k] = json.loads(v)
                    except json.JSONDecodeError:
                        logger.warning(f"属性 '{k}' 的值不是有效的 JSON 字符串: {v}")
                        returned_properties[k] = v
                else:
                    returned_properties[k] = v

        return EntityModel(
            id=result_data["id"],
            name=result_data["name"],
            email=result_data["email"],
            type=result_data["type"],
            properties=returned_properties,
            model_id=result_data["model_id"],
        )

    def delete_entity(self, entity_id: str) -> Dict[str, Any]:
        """
        根据 ID 删除实体节点及其所有关系。
        """
        query = """
        MATCH (e:Entity {id: $entity_id})
        DETACH DELETE e
        """
        parameters = {"entity_id": entity_id}
        self.db.execute_query(query, parameters)

        # 验证实体是否真的被删除：再次尝试匹配该实体
        verify_query = """
                MATCH (e:Entity {id: $entity_id})
                RETURN e.id AS id
                """
        verification_result = self.db.execute_query(verify_query, parameters)

        if not verification_result:
            # 如果查询结果为空，说明实体已被成功删除
            return {"message": f"实体 {entity_id} 已删除"}
        else:
            # 如果查询结果不为空，说明实体仍在，删除失败
            raise ValueError(f"实体 {entity_id} 仍在，删除失败")

    def create_relation(self, relation_data: RelationModel) -> RelationModel:
        """
        在两个实体之间创建一个新的关系。
        """
        relation_id = relation_data.id if relation_data.id else str(uuid.uuid4())

        if not re.fullmatch(r'^[a-zA-Z_][a-zA-Z0-9_]*$', relation_data.type):
            relation_data.type = f"`{relation_data.type}`"
        all_properties = {
            "id": relation_id,
            "type": relation_data.type
        }
        all_properties.update(relation_data.properties)

        query = f"""
        MATCH (source:Entity {{id: $source_id}}), (target:Entity {{id: $target_id}})
        CREATE (source)-[r:{relation_data.type} $props]->(target)
        RETURN r.id AS id, type(r) AS type, properties(r) AS properties,
               source.id AS source_id, target.id AS target_id,
               {"$model_id" if relation_data.model_id else "null"} AS model_id
        """
        parameters = {
            "source_id": relation_data.source_id,
            "target_id": relation_data.target_id,
            "props": all_properties,
            "model_id": relation_data.model_id
        }
        results = self.db.execute_query(query, parameters)
        if not results:
            raise ValueError(
                f"创建关系失败。检查源和目标实体 ID： {relation_data.source_id}, {relation_data.target_id}")

        result_data = results[0]
        returned_properties = {k: v for k, v in result_data["properties"].items() if k not in ["id", "type"]}
        return RelationModel(
            id=result_data["id"],
            source_id=str(result_data["source_id"]),
            target_id=str(result_data["target_id"]),
            type=result_data["type"],
            properties=returned_properties,
            model_id=result_data["model_id"]
        )

    def create_bulk_relations(self, relations_data: List[RelationModel]) -> List[RelationModel]:
        """
        创建多个关系。
        """
        return [self.create_relation(relation) for relation in relations_data]

    def get_relation(self, relation_id: str) -> RelationModel:
        """
        根据 ID 获取一个关系。
        """
        query = """
        MATCH (source)-[r]->(target)
        WHERE r.id = $relation_id

        // ⚠️ 修正：将 OPTIONAL MATCH 提升到 WITH 之外，以便后续 CASE 表达式使用它们的结果
        OPTIONAL MATCH (m_source:Model)-[:HAS_ENTITY]->(source)
        OPTIONAL MATCH (m_target:Model)-[:HAS_ENTITY]->(target)

        WITH source, r, target, m_source, m_target, // 将 m_source 和 m_target 传递到 WITH 子句中
             CASE
                 // 情况1: 如果关系本身就是 HAS_ENTITY 并且是从 Model 指向 Entity
                 // 使用 'Model' IN labels(source) 更通用和安全
                 WHEN TYPE(r) = 'HAS_ENTITY' AND 'Model' IN labels(source) AND 'Entity' IN labels(target) THEN source.id
                 // 情况2: 如果关系是实体之间的关系 (非 HAS_ENTITY)，找到拥有源实体或目标实体的模型
                 ELSE COALESCE(m_source.id, m_target.id) // 直接使用 m_source.id 和 m_target.id
             END AS calculated_model_id

        RETURN
            r.id AS id,
            TYPE(r) AS type,
            properties(r) AS properties,
            source.id AS source_id,
            target.id AS target_id,
            calculated_model_id AS model_id // 使用计算出的 model_id
        """
        parameters = {"relation_id": relation_id}
        results = self.db.execute_query(query, parameters)
        if not results:
            raise ValueError(f"关系 {relation_id} 不存在")

        result_data = results[0]
        returned_properties = {k: v for k, v in result_data["properties"].items() if k not in ["id", "type"]}
        return RelationModel(
            id=result_data["id"],
            source_id=str(result_data["source_id"]),
            target_id=str(result_data["target_id"]),
            type=result_data["type"],
            properties=returned_properties,
            model_id=result_data["model_id"]
        )

    def get_all_relations(self, model_id: str) -> List[RelationModel]:
        """
        获取数据库中所有关系节点的列表。
        """
        query = """
        MATCH (source)-[r]->(target)

        // 尝试找到源实体所属的模型
        OPTIONAL MATCH (m_source:Model)-[:HAS_ENTITY]->(source)
        // 尝试找到目标实体所属的模型
        OPTIONAL MATCH (m_target:Model)-[:HAS_ENTITY]->(target)

        WITH source, r, target, m_source, m_target,
             CASE
                 // 情况1: 如果关系本身就是 HAS_ENTITY 并且是从 Model 指向 Entity
                 // 此时，源节点 (source) 就是模型本身
                 WHEN TYPE(r) = 'HAS_ENTITY' AND 'Model' IN labels(source) AND 'Entity' IN labels(target) THEN source.id
                 // 情况2: 如果关系是实体之间的关系 (非 HAS_ENTITY)，
                 // 则尝试从源实体或目标实体所关联的模型中获取 ID
                 ELSE COALESCE(m_source.id, m_target.id)
             END AS calculated_model_id

        // ⚠️ 核心修正：在 Cypher 中添加 WHERE 子句进行过滤
        // 排除掉那些 source_id 等于 calculated_model_id 的关系
        // WHERE NOT (TYPE(r) = 'HAS_ENTITY' AND 'Model' IN labels(source) AND source.id = calculated_model_id)
        // AND calculated_model_id = $model_id
              // 另一种等效的排除方式，更通用：
         WHERE NOT (source.id = calculated_model_id AND calculated_model_id IS NOT NULL)

        RETURN
            r.id AS id,
            TYPE(r) AS type,
            properties(r) AS properties,
            source.id AS source_id, // 保持命名不变
            target.id AS target_id, // 保持命名不变
            calculated_model_id AS model_id
        """
        parameters = {"model_id": model_id}
        results = self.db.execute_query(query, parameters)

        relations = []
        for result_data in results:
            if result_data["model_id"] == result_data["source_id"]:
                continue
            if result_data["model_id"] != model_id:
                continue
            returned_properties = {k: v for k, v in result_data["properties"].items() if
                                   k not in ["id", "type"]}  # 排除 id 属性
            relations.append(RelationModel(
                id=result_data["id"],
                source_id=result_data["source_id"],
                target_id=result_data["target_id"],
                type=result_data["type"],
                properties=returned_properties,
                model_id=result_data["model_id"]
            ))
        return relations

    def update_relation(self, relation_id: str, update_data: Dict[str, Any]) -> RelationModel:
        """
        更新关系的属性和/或类型。
        """
        current_relation = self.get_relation(relation_id)

        props_to_set = {}
        new_relation_type = update_data.get('type', current_relation.type)

        if 'properties' in update_data:
            updated_dynamic_props = current_relation.properties.copy()
            updated_dynamic_props.update(update_data['properties'])
            props_to_set.update(updated_dynamic_props)

        if current_relation.type != new_relation_type:
            if not re.fullmatch(r'^[a-zA-Z_][a-zA-Z0-9_]*$', new_relation_type):
                new_relation_type = f"`{new_relation_type}`"
            query = f"""
            MATCH (source)-[r]->(target)
            WHERE r.id = $relation_id
            DELETE r // 删除旧关系
    
            // 创建新关系，保留旧 ID 或生成新 ID (这里选择保留旧 ID)
            CREATE (source)-[new_r:{new_relation_type} $props_to_apply]->(target)
            WITH source, new_r AS r, target // 将新创建的关系命名为 r，以便后续逻辑统一
    
            // 现在计算 model_id，逻辑与之前相同
            OPTIONAL MATCH (m_source:Model)-[:HAS_ENTITY]->(source)
            OPTIONAL MATCH (m_target:Model)-[:HAS_ENTITY]->(target)
    
            WITH source, r, target, m_source, m_target,
                 CASE
                     WHEN TYPE(r) = 'HAS_ENTITY' AND 'Model' IN labels(source) AND 'Entity' IN labels(target) THEN source.id
                     ELSE COALESCE(m_source.id, m_target.id)
                 END AS calculated_model_id
    
            RETURN
                r.id AS id,
                TYPE(r) AS type,
                properties(r) AS properties,
                startNode(r).id AS source_id,
                endNode(r).id AS target_id,
                calculated_model_id AS model_id
            """
            parameters = {
                "relation_id": relation_id,
                "props_to_apply": {**props_to_set, "id": relation_id}
            }
        else:
            # 关系类型未变化，只更新属性
            query = """
            MATCH (source)-[r]->(target)
            WHERE r.id = $relation_id
            SET r += $props_to_set // 只更新属性

            WITH source, r, target // 传递变量

            // 计算 model_id，逻辑与之前相同
            OPTIONAL MATCH (m_source:Model)-[:HAS_ENTITY]->(source)
            OPTIONAL MATCH (m_target:Model)-[:HAS_ENTITY]->(target)

            WITH source, r, target, m_source, m_target,
                 CASE
                     WHEN TYPE(r) = 'HAS_ENTITY' AND 'Model' IN labels(source) AND 'Entity' IN labels(target) THEN source.id
                     ELSE COALESCE(m_source.id, m_target.id)
                 END AS calculated_model_id

            RETURN
                r.id AS id,
                TYPE(r) AS type,
                properties(r) AS properties,
                startNode(r).id AS source_id,
                endNode(r).id AS target_id,
                calculated_model_id AS model_id
            """
            parameters = {
                "relation_id": relation_id,
                "props_to_set": props_to_set
            }
        results = self.db.execute_query(query, parameters)
        if not results:
            raise ValueError(f"RelationModel with ID '{relation_id}' not found or failed to update.")

        result_data = results[0]
        returned_properties = {k: v for k, v in result_data["properties"].items() if k not in ["id", "type"]}
        return RelationModel(
            id=result_data["id"],
            source_id=str(result_data["source_id"]),
            target_id=str(result_data["target_id"]),
            type=result_data["type"],
            properties=returned_properties,
            model_id=result_data["model_id"]
        )

    def delete_relation(self, relation_id: str) -> Dict[str, Any]:
        """
        根据 ID 删除关系。
        """
        query = """
        MATCH ()-[r]->()
        WHERE r.id = $relation_id
        DELETE r
        """
        parameters = {"relation_id": relation_id}
        self.db.execute_query(query, parameters)
        try:
            self.get_relation(relation_id)
            raise ValueError(f"删除关系失败{relation_id}")
        except ValueError:
            return {"message": f"删除关系成功{relation_id}"}

    '''
    知识融合
    '''

    def merge_entities(self, entity_id_to_keep: str, entity_ids_to_merge: List[str]) -> None:
        """
        合并多个实体到保留的实体

        Args:
            entity_ids_to_merge: 要合并的实体 ID 列表
            entity_id_to_keep: 要保留的实体 ID
        """
        if entity_id_to_keep not in entity_ids_to_merge:
            raise ValueError("要保留的实体ID必须是待合并实体之一")

        # 1. 验证实体存在性(使用读操作)
        keep_entity = self.db.execute_query(
            "MATCH (e:Entity {id: $id}) RETURN e",
            {"id": entity_id_to_keep}
        )

        if not keep_entity:
            raise ValueError(f"保留实体 {entity_id_to_keep} 不存在")

        for merge_id in entity_ids_to_merge:
            if merge_id == entity_id_to_keep:
                continue

            merge_entity = self.db.execute_query(
                "MATCH (e:Entity {id: $id}) RETURN e",
                {"id": merge_id}
            )

            if not merge_entity:
                logger.warning(f"警告: 实体 {merge_id} 不存在，跳过")
                continue

        # 2. 合并属性(尝试使用APOC，如果失败则回退到简单属性合并)
        try:
            # 尝试使用APOC合并属性
            self.db.execute_query("""
            MATCH (keep:Entity {id: $keep_id}), (merge:Entity {id: $merge_id})
            CALL apoc.map.merge(keep, merge) YIELD value
            SET keep = value
            """, {"keep_id": entity_id_to_keep, "merge_id": merge_id})
            logger.info("使用APOC成功合并属性")
        except Exception as e:
            logger.warning(f"APOC合并属性失败，尝试简单合并: {str(e)}")
            # 回退到简单属性合并(只合并name和email属性作为示例)
            # 获取保留实体的当前属性
            keep_props = self.db.execute_query(
                "MATCH (e:Entity {id: $id}) RETURN e.name AS name, e.email AS email",
                {"id": entity_id_to_keep}
            )

            if not keep_props:
                logger.error(f"无法获取保留实体 {entity_id_to_keep} 的属性")
                raise ValueError(f"无法获取保留实体 {entity_id_to_keep} 的属性")

            keep_name = keep_props[0].get('name', None)
            keep_email = keep_props[0].get('email', None)

            # 获取要合并的第一个实体的属性(假设只合并一个实体作为示例，可以根据需求扩展)
            # 这里我们仅合并第一个要合并的实体，您可以根据需要扩展为合并多个
            merge_ids_to_process = [mid for mid in entity_ids_to_merge if mid != entity_id_to_keep]
            if not merge_ids_to_process:
                logger.warning("没有需要合并的实体")
                return

            merge_id = merge_ids_to_process[0]  # 仅合并第一个实体
            merge_props = self.db.execute_query(
                "MATCH (e:Entity {id: $id}) RETURN e.name AS name, e.email AS email",
                {"id": merge_id}
            )

            if not merge_props:
                logger.warning(f"无法获取合并实体 {merge_id} 的属性，跳过")
                return

            merge_name = merge_props[0].get('name', None)
            merge_email = merge_props[0].get('email', None)

            # 合并属性(保留实体的属性优先)
            merged_name = merge_name if not keep_name else keep_name
            merged_email = merge_email if not keep_email else keep_email

            # 更新保留实体的属性
            self.db.execute_query(
                "MATCH (e:Entity {id: $id}) SET e.name = $name, e.email = $email",
                {"id": entity_id_to_keep, "name": merged_name, "email": merged_email}
            )
            logger.info("简单合并属性完成")

        # 3. 转移关系(使用写操作)
        # 动态处理不同类型的关系，不转移关系属性
        for merge_id in entity_ids_to_merge:
            if merge_id == entity_id_to_keep:
                continue

            # 获取所有出站关系类型
            out_relationship_types = self.db.execute_query("""
            MATCH (merge:Entity {id: $merge_id})-[r]->(target)
            RETURN DISTINCT type(r) AS rel_type
            """, {"merge_id": merge_id})

            for rel_type in out_relationship_types:
                rel_type_str = rel_type.get('rel_type', None)
                if not rel_type_str:
                    continue
                # 转移出站关系: merge-[r:rel_type]->target 变为 keep-[new_r:rel_type]->target
                self.db.execute_query(f"""
                MATCH (merge:Entity {{id: $merge_id}})-[r:{rel_type_str}]->(target)
                MERGE (keep:Entity {{id: $keep_id}})-[new_r:{rel_type_str}]->(target)
                DELETE r
                """, {"merge_id": merge_id, "keep_id": entity_id_to_keep})

            # 获取所有入站关系类型
            in_relationship_types = self.db.execute_query("""
            MATCH (target)-[r]->(merge:Entity {id: $merge_id})
            RETURN DISTINCT type(r) AS rel_type
            """, {"merge_id": merge_id})

            for rel_type in in_relationship_types:
                rel_type_str = rel_type.get('rel_type', None)
                if not rel_type_str:
                    continue
                # 转移入站关系: target-[r:rel_type]->merge 变为 target-[new_r:rel_type]->keep
                self.db.execute_query(f"""
                MATCH (target)-[r:{rel_type_str}]->(merge:Entity {{id: $merge_id}})
                MERGE (target)-[new_r:{rel_type_str}]->(keep:Entity {{id: $keep_id}})
                DELETE r
                """, {"merge_id": merge_id, "keep_id": entity_id_to_keep})

    '''
        智能问答
        '''

    def _extract_entities(self, question: str) -> List[str]:
        """改进的实体识别方法，专注于人名识别"""
        words = jieba.lcut(question)

        # 常见中文姓氏(单姓和复姓)
        surnames = {
            '李', '张', '王', '赵', '陈', '刘', '杨', '黄', '周', '吴',  # 单姓
            '欧阳', '司马', '诸葛', '东方', '皇甫', '慕容', '宇文', '长孙'  # 复姓
        }

        # 常见非实体词(停用词)
        stop_words = {'关系', '和', '与', '的', '是', '在', '有', '等'}

        # 第一步：提取所有可能的人名候选
        candidates = []
        n = len(words)
        i = 0

        while i < n:
            # 情况1：匹配复姓+名字(2-3字)
            if i < n and words[i] in {'欧阳', '司马', '诸葛', '东方', '皇甫', '慕容', '宇文', '长孙'}:
                if i + 1 < n:
                    # 复姓+单字名(2字人名)
                    candidate = words[i] + words[i + 1]
                    if len(candidate) <= 4:  # 限制最大长度
                        candidates.append(candidate)
                    i += 2
                    continue

            # 情况2：匹配单姓+名字(2-3字)
            if i < n and len(words[i]) == 1 and words[i] in {'李', '张', '王', '赵', '陈', '刘', '杨', '黄', '周', '吴'}:
                # 尝试组合1-2个后续字
                for j in range(1, 3):
                    if i + j < n:
                        candidate = words[i] + ''.join(words[i + 1:i + j + 1])
                        if 2 <= len(candidate) <= 4:  # 限制长度
                            candidates.append(candidate)
                        break  # 只取最长的可能匹配
                i += 1
                continue

            # 情况3：直接匹配2-3字词(可能是人名)
            if i < n and 2 <= len(words[i]) <= 3:
                candidates.append(words[i])

            i += 1

        # 第二步：过滤候选词
        entities = []
        for candidate in candidates:
            # 条件1：不在停用词列表中
            if candidate in stop_words:
                continue

            # 条件2：看起来像人名(简单启发式规则)
            # 这里可以添加更多规则，如常见名字用字等
            entities.append(candidate)

        return entities

    def is_stop_word(self, word: str) -> bool:
        """简单的停用词判断"""
        stop_words = ["的", "是", "在", "和", "与", "谁", "什么", "的", "了", "着"]
        return word in stop_words

    # 查询函数实现
    def query_by_name(self, question: str, entities: List[Tuple[str, str]]) -> List[Dict[str, Any]]:
        """按名称查询人物"""

        # entities = self._extract_entities(question)
        entities = [name for name, _ in entities]
        if not entities:
            logger.warning("未从问题中提取到实体名称")
            return []

        logger.info(f"查询名称: {entities}")
        query = """
                    MATCH (m:Model)-[:HAS_ENTITY]->(e:Entity)
                    WHERE e.name IN $names
                    RETURN 
                        e.id AS id, 
                        e.name AS name, 
                        e.email AS email, 
                        e.type AS type, 
                        properties(e) AS properties, 
                        m.id AS model_id
                    """

        result = self.db.execute_query(query, {"names": entities})
        records = []
        for record in result:
            # 确保所有字段都被正确提取
            record_data = {
                "id": record["id"],
                "name": record["name"],
                "email": record["email"],
                "type": record["type"],
                "properties": record["properties"],
                "model_id": record["model_id"]
            }
            records.append(record_data)

        if not records:
            logger.warning(f"未找到匹配的人物: {entities}")
            return []

        return records

    def query_by_property(self, question: str, entities: List[Tuple[str, str]]) -> List[Dict[str, Any]]:
        """查询人物属性"""
        entities = [name for name, _ in entities]  # 结果: ["赵六", "张嘉译"]
        # entities = self._extract_entities(question)
        if not entities:
            logger.warning("未从问题中提取到实体名称")
            return []

        name = entities[0]
        logger.info(f"查询属性: {name}")
        query = """
                    MATCH (m:Model)-[:HAS_ENTITY]->(n:Entity)
                    WHERE n.name = $name
                    RETURN 
                        n.id AS id, 
                        n.name AS name, 
                        n.email AS email, 
                        n.type AS type, 
                        properties(n) AS properties, 
                        m.id AS model_id
                    """

        result = self.db.execute_query(query, {"name": name})
        print("result is ", result)
        records = []
        for record in result:
            # 确保所有字段都被正确提取
            record_data = {
                "id": record["id"],
                "name": record["name"],
                "email": record["email"],
                "type": record["type"],
                "properties": record["properties"],
                "model_id": record["model_id"]
            }
            records.append(record_data)

        if not records:
            logger.warning(f"未找到人物: {name}")
            return []

        return records

    def query_relationship(self, question: str, entities: List[Tuple[str, str]]) -> dict[str, str]:
        """查询两个人物之间的关系路径"""

        # entities = self._extract_entities(question)
        entities = [name for name, _ in entities]
        if len(entities) < 2:
            logger.warning("关系路径查询需要至少两个人物名称")
            return []

        name1, name2 = entities[0], entities[1]
        logger.info(f"查询关系路径: {name1} 和 {name2}")

        query_entity = """
                            MATCH (m:Model)-[:HAS_ENTITY]->(e:Entity)
                            WHERE e.name IN $names
                            RETURN 
                                e.id AS id, 
                                e.name AS name, 
                                e.email AS email, 
                                e.type AS type, 
                                properties(e) AS properties, 
                                m.id AS model_id
                            """

        entity_result = self.db.execute_query(query_entity, {"names": entities})

        # 从查询结果中提取 name1 和 name2 对应的 id
        entity_id_map = {entity["name"]: entity["id"] for entity in entity_result}

        # 确保两个名称都找到了对应的实体
        if name1 not in entity_id_map or name2 not in entity_id_map:
            logger.error(f"未能找到名称 {name1} 或 {name2} 对应的实体")
            return {"error": f"未能找到名称 {name1} 或 {name2} 对应的实体"}

        id1 = entity_id_map[name1]
        id2 = entity_id_map[name2]

        logger.info(f"找到实体ID: {name1} -> {id1}, {name2} -> {id2}")

        # 查询所有模型下的关系
        query = """
                    MATCH (a:Entity {id: $id1})-[r]-(b:Entity {id: $id2})
                    RETURN 
                    a.id AS source_id, 
                    a.name AS source_name, 
                    type(r) AS relation_type, 
                    properties(r) AS relation_properties, 
                    b.id AS target_id, 
                    b.name AS target_name
                        """

        result = self.db.execute_query(query, {"id1": id1, "id2": id2})
        print("result relationsss", result)

        return result  # 确保返回的是列表

    '''
    智能引擎
    '''

    def add_document(self, title: str, content: str, entities: List[Dict], person_info: Dict = None):
        """
        添加文档到知识图谱
        :param title: 文档标题
        :param content: 文档内容
        :param entities: 实体列表 [{"name": "实体名", "type": "类型"}, ...]
        :param person_info: 人物详细信息（可选）
        """
        # 1. 创建或获取文档节点并设置内容
        self.db.execute_query("""
            MERGE (d:Document {title: $title})
            SET d.content = $content
        """, {"title": title, "content": content})

        # 2. 批量处理实体关系（使用UNWIND优化循环）
        if entities:
            self.db.execute_query("""
                UNWIND $entities AS entity
                MERGE (e:EntitySearch {name: entity.name, type: entity.type})
                MERGE (d:Document {title: $title})
                MERGE (d)-[:CONTAINS_ENTITY]->(e)
            """, {"title": title, "entities": entities})

        # 3. 处理人物信息（可选）
        if person_info:
            # 提取人物基础属性（过滤无效字段）
            person_props = {k: v for k, v in person_info.items()
                            if k in ["name", "birth_year", "death_year", "nationality"]}
            # 3.1 创建或更新人物节点
            self.db.execute_query("""
                MERGE (p:Person {name: $name})
                SET p.birth_year = $birth_year,
                    p.death_year = $death_year,
                    p.nationality = $nationality
            """, person_props)

            # 3.2 关联文档与人物
            self.db.execute_query("""
                MATCH (d:Document {title: $title}), (p:Person {name: $person_name})
                MERGE (d)-[:DESCRIBES]->(p)
            """, {"title": title, "person_name": person_info["name"]})

            # 3.3 批量添加人物成就（如果有）
            if "achievements" in person_info and person_info["achievements"]:
                achievements = person_info["achievements"]
                self.db.execute_query("""
                    UNWIND $achievements AS ach
                    MERGE (a:Achievement {name: ach.name, year: ach.year})
                    MERGE (p:Person {name: $person_name})
                    MERGE (p)-[:ACHIEVED]->(a)
                """, {"person_name": person_info["name"], "achievements": achievements})

            # 3.4 批量添加人物相关事件（如果有）
            if "related_events" in person_info and person_info["related_events"]:
                events = person_info["related_events"]
                self.db.execute_query("""
                    UNWIND $events AS evt
                    MERGE (e:Event {name: evt.name, year: evt.year})
                    MERGE (p:Person {name: $person_name})
                    MERGE (p)-[:INVOLVED_IN]->(e)
                """, {"person_name": person_info["name"], "events": events})

    def search(self, search_input: str, **kwargs):
        """
        统一智能搜索方法
        :param search_input: 搜索输入(可以是实体名、人物名、关键词或自然语言问题)
        :param kwargs: 可选参数，用于指定搜索类型或过滤条件
        :return: 根据输入内容自动判断返回最相关的结果
        """
        # 1. 处理概括性查询
        if self._is_general_query(search_input):
            general_result = self._handle_general_query(search_input)
            if general_result:
                return self._format_response(general_result)

        # 2. 处理自然语言问题
        if self._is_question(search_input):
            question_result = self._handle_question(search_input)
            if question_result:
                return self._format_response(question_result)

        # 3. 检查是否是明确的人物搜索
        if self._is_person_search(search_input, kwargs):
            return self._format_response(self._search_person(search_input))

        # 4. 检查是否是明确的实体搜索
        if self._is_entity_search(search_input, kwargs):
            return self._format_response(self._search_entity(search_input, kwargs.get('entity_type')))

        # 5. 检查是否是成就搜索
        if self._is_achievement_search(search_input):
            return self._format_response(self._search_by_achievement(search_input))

        # 6. 默认智能搜索
        return self._format_response(self._smart_search(search_input, **kwargs))

    def _is_general_query(self, search_input: str) -> bool:
        """判断是否是概括性查询"""
        general_queries = ["有哪些", "列表", "全部", "所有"]
        return any(q in search_input for q in general_queries)

    def _handle_general_query(self, search_input: str) -> Optional[Dict]:
        """处理概括性查询"""
        # 处理"科学家有哪些"这类查询
        if "科学家有哪些" in search_input or "科学家列表" in search_input:
            nationality = search_input.replace("科学家有哪些", "").replace("科学家列表", "").strip()
            return self._search_scientists_by_nationality(nationality or "中国")

        # 处理"奖项有哪些"查询
        if "奖项有哪些" in search_input or "奖项列表" in search_input:
            return self._search_all_awards()

        # 可以添加其他概括性查询处理
        return None

    def _search_scientists_by_nationality(self, nationality: str, limit: int = 50) -> Dict:
        """根据国籍搜索科学家"""
        result = self.db.execute_query("""
            MATCH (p:Person {nationality: $nationality})
            OPTIONAL MATCH (p)-[:ACHIEVED]->(a:Achievement)
            WITH p, COLLECT(a.name) AS achievements
            RETURN p.name AS name, p.birth_year AS birth_year, achievements
            ORDER BY p.name
            LIMIT $limit
        """, {"nationality": nationality, "limit": limit})

        if not result:
            return {"type": "scientists_list", "result": [], "message": f"未找到{nationality}科学家"}

        return {
            "type": "scientists_list",
            "result": [dict(item) for item in result],
            "nationality": nationality,
            "count": len(result)
        }

    def _search_all_awards(self, limit: int = 50) -> Dict:
        """搜索所有奖项"""
        result = self.db.execute_query("""
            MATCH (a:Achievement)
            WHERE a.name CONTAINS '奖'
            RETURN DISTINCT a.name AS award_name
            ORDER BY a.name
            LIMIT $limit
        """, {"limit": limit})

        return {
            "type": "awards_list",
            "result": [dict(item) for item in result],
            "count": len(result)
        }

    def _is_question(self, search_input: str) -> bool:
        """判断是否是自然语言问题"""
        question_words = ["是谁", "是谁的", "什么是", "什么是", "谁发明了", "谁发现了", "？", "?"]
        return any(word in search_input for word in question_words)

    def _handle_question(self, search_input: str) -> Optional[Dict]:
        """处理自然语言问题"""
        # 处理"是谁"类问题
        if "是谁" in search_input:
            entity = search_input.replace("是谁", "").replace("?", "").replace("？", "").strip()
            persons = self._search_person_by_title(entity)
            if persons:
                return {"type": "person_by_title", "result": persons, "title": entity}

        # 处理"什么是"类问题
        if "什么是" in search_input:
            concept = search_input.replace("什么是", "").replace("?", "").replace("？", "").strip()
            entity = self._search_entity(concept)
            if entity["result"]:
                return entity

        # 处理"谁发明了"类问题
        if "谁发明了" in search_input or "谁发现了" in search_input:
            invention = search_input.replace("谁发明了", "").replace("谁发现了", "").replace("?", "").replace("？", "").strip()
            persons = self._search_inventor(invention)
            if persons:
                return {"type": "inventors", "result": persons, "invention": invention}

        return None

    def _search_person_by_title(self, title: str) -> List[Dict]:
        """通过称号搜索人物"""
        # 尝试直接匹配成就名称
        result = self.db.execute_query("""
            MATCH (p:Person)-[:ACHIEVED]->(a:Achievement {name: $title})
            RETURN p.name AS name, a.year AS year
        """, {"title": title})

        if result:
            return [dict(item) for item in result]

        # 尝试在文档内容中搜索
        result = self.db.execute_query("""
            MATCH (d:Document)
            WHERE d.content CONTAINS $title
            MATCH (d)-[:DESCRIBES]->(p:Person)
            RETURN DISTINCT p.name AS name
        """, {"title": title})

        return [dict(item) for item in result]

    def _search_inventor(self, invention: str) -> List[Dict]:
        """搜索发明者"""
        result = self.db.execute_query("""
            MATCH (p:Person)-[:ACHIEVED]->(a:Achievement)
            WHERE a.name CONTAINS $invention OR 
                  (p)-[:INVOLVED_IN]->(:Event {name: $invention})
            RETURN p.name AS name, a.name AS achievement
        """, {"invention": invention})

        return [dict(item) for item in result]

    def _is_person_search(self, search_input: str, kwargs: Dict) -> bool:
        """判断是否应该执行人物搜索"""
        if kwargs.get('search_type') == 'person':
            return True

        result = self.db.execute_query("""
            MATCH (p:Person {name: $name})
            RETURN p LIMIT 1
        """, {"name": search_input})
        return len(result) > 0

    def _is_entity_search(self, search_input: str, kwargs: Dict) -> bool:
        """判断是否应该执行实体搜索"""
        if kwargs.get('search_type') == 'entity':
            return True

        result = self.db.execute_query("""
            MATCH (e:EntitySearch {name: $name})
            RETURN e LIMIT 1
        """, {"name": search_input})
        return len(result) > 0

    def _is_achievement_search(self, search_input: str) -> bool:
        """判断是否是成就搜索"""
        return "奖" in search_input or "成就" in search_input or "发现" in search_input

    def _search_person(self, person_name: str) -> Dict:
        """搜索人物详细信息"""
        result = self.db.execute_query("""
            MATCH (p:Person {name: $name})
            OPTIONAL MATCH (d:Document)-[:DESCRIBES]->(p)
            RETURN p, COLLECT(DISTINCT d.title) AS documents
        """, {"name": person_name})

        if not result:
            return {"type": "person", "result": None, "message": "未找到该人物"}

        person_data = dict(result[0]["p"].items())
        person_data["related_documents"] = result[0]["documents"]

        achievements = self.db.execute_query("""
            MATCH (p:Person {name: $name})-[:ACHIEVED]->(a:Achievement)
            RETURN a.name AS name, a.year AS year
            ORDER BY a.year
        """, {"name": person_name})
        person_data["achievements"] = [dict(ach) for ach in achievements]

        events = self.db.execute_query("""
            MATCH (p:Person {name: $name})-[:INVOLVED_IN]->(e:Event)
            RETURN e.name AS name, e.year AS year
            ORDER BY e.year
        """, {"name": person_name})
        person_data["related_events"] = [dict(evt) for evt in events]

        return {
            "type": "person",
            "result": person_data,
            "related_entities": self._find_related_entities(person_name)
        }

    def _search_entity(self, entity_name: str, entity_type: str = None) -> Dict:
        """搜索实体信息"""
        if entity_type:
            result = self.db.execute_query("""
                MATCH (e:EntitySearch {name: $name, type: $type})
                OPTIONAL MATCH (d:Document)-[:CONTAINS_ENTITY]->(e)
                RETURN e, COLLECT(DISTINCT d.title) AS documents
            """, {"name": entity_name, "type": entity_type})
        else:
            result = self.db.execute_query("""
                MATCH (e:EntitySearch {name: $name})
                OPTIONAL MATCH (d:Document)-[:CONTAINS_ENTITY]->(e)
                RETURN e, COLLECT(DISTINCT d.title) AS documents
            """, {"name": entity_name})

        if not result:
            return {"type": "entity", "result": None, "message": "未找到该实体"}

        entity_data = dict(result[0]["e"].items())
        entity_data["related_documents"] = result[0]["documents"]

        return {
            "type": "entity",
            "result": entity_data,
            "related_persons": self._find_related_persons(entity_name),
            "related_entities": self._find_related_entities(entity_name)
        }

    def _search_by_achievement(self, achievement_name: str) -> Dict:
        """根据成就搜索"""
        result = self.db.execute_query("""
            MATCH (p:Person)-[:ACHIEVED]->(a:Achievement)
            WHERE a.name CONTAINS $name
            RETURN p.name AS person_name, a.name AS achievement, a.year AS year
            ORDER BY a.year
        """, {"name": achievement_name})

        if not result:
            return {"type": "achievement", "result": None, "message": "未找到相关成就"}

        return {
            "type": "achievement",
            "result": [dict(item) for item in result],
            "suggested_queries": [
                {"type": "person", "query": item["person_name"]}
                for item in result
            ]
        }

    def _smart_search(self, search_input: str, **kwargs) -> Dict:
        """智能搜索路由"""
        results = []

        person_result = self._search_person(search_input)
        if person_result["result"]:
            results.append((3.0, person_result))

        entity_result = self._search_entity(search_input)
        if entity_result["result"]:
            results.append((2.0, entity_result))

        achievement_result = self._search_by_achievement(search_input)
        if achievement_result["result"]:
            results.append((1.5, achievement_result))

        search_result = self._semantic_search(search_input, kwargs.get('limit', 5))
        if search_result["documents"] or search_result["entities"]:
            results.append((1.0, {
                "type": "search",
                "result": search_result
            }))

        if not results:
            return {"type": "unknown", "result": None, "message": "未找到相关信息"}

        results.sort(key=lambda x: x[0], reverse=True)
        best_result = results[0][1]

        if len(results) > 1:
            best_result["suggested_queries"] = [
                {"type": res[1]["type"], "query": search_input}
                for res in results[1:] if res[1]["result"]
            ]

        return best_result

    def _find_related_entities(self, entity_name: str, limit: int = 5) -> List[Dict]:
        """查找相关实体"""
        result = self.db.execute_query("""
            MATCH (e1:EntitySearch {name: $name})<-[:CONTAINS_ENTITY]-(d:Document)-[:CONTAINS_ENTITY]->(e2:EntitySearch)
            WHERE e1 <> e2
            RETURN DISTINCT e2.name AS name, e2.type AS type, COUNT(*) AS connection_strength
            ORDER BY connection_strength DESC
            LIMIT $limit
        """, {"name": entity_name, "limit": limit})
        return [dict(ent) for ent in result]

    def _find_related_persons(self, entity_name: str, limit: int = 5) -> List[Dict]:
        """查找相关人物"""
        result = self.db.execute_query("""
            MATCH (e:EntitySearch {name: $name})<-[:CONTAINS_ENTITY]-(d:Document)-[:DESCRIBES]->(p:Person)
            RETURN DISTINCT p.name AS name, COLLECT(DISTINCT d.title) AS related_documents
            LIMIT $limit
        """, {"name": entity_name, "limit": limit})
        return [dict(person) for person in result]

    def _semantic_search(self, query: str, limit: int = 5) -> Dict:
        """语义搜索"""
        docs = self.db.execute_query("""
            MATCH (d:Document)
            WHERE d.title CONTAINS $query OR d.content CONTAINS $query
            RETURN d.title AS title, d.content AS content
            LIMIT $limit
        """, {"query": query, "limit": limit})

        entities = self.db.execute_query("""
            MATCH (e:EntitySearch)
            WHERE e.name CONTAINS $query
            RETURN e.name AS name, e.type AS type
            LIMIT $limit
        """, {"query": query, "limit": limit})

        return {
            "documents": [dict(doc) for doc in docs],
            "entities": [dict(ent) for ent in entities]
        }

    def _format_response(self, data: Dict) -> Dict:
        return data

    def assemble_compatible_search_result(self, search_data: dict) -> str:
        """
        兼容多种搜索结果类型的智能组装函数
        :param search_data: 搜索返回的结构化数据
        :return: 自然语言描述的搜索结果
        """
        # 基础数据验证
        if not search_data or 'result' not in search_data:
            return "未找到相关信息"

        data = search_data
        if not data:
            return "未找到相关信息"

        # 根据不同类型调用对应的组装函数
        if 'type' not in data:
            return "未识别结果类型"

        result_type = data['type']

        if result_type == 'person':
            return self.assemble_person_search_result(data)
        elif result_type == 'search':
            return self.assemble_document_search_result(data)
        elif result_type == 'achievement':
            return self.assemble_achievement_result(data)
        elif result_type == 'entity':
            return self.assemble_entity_result(data)
        elif result_type == 'inventors':
            return self.assemble_inventors_result(data)
        elif result_type == 'scientists_list':
            return self.assemble_scientists_list_result(data)
        elif result_type == 'person_by_title':
            return self.assemble_person_by_title_result(data)
        elif result_type == 'awards_list':  # 新增的类型判断
            return self.assemble_awards_list_result(data)
        else:
            return "未支持的结果类型: {}".format(result_type)

    def assemble_person_search_result(self, person_data: dict) -> str:
        """
        组装人物搜索结果
        """
        result = person_data.get('result', {})
        if not result:
            return "未找到相关人员详细信息"

        # 提取基础信息
        name = result.get('name', '未知人物')
        nationality = result.get('nationality', '未知国籍')
        birth_year = result.get('birth_year')
        death_year = result.get('death_year')

        # 构建基础信息部分
        base_info_parts = [f"{name}({nationality})"]
        if birth_year and death_year:
            base_info_parts.append(f"({birth_year}年-{death_year}年)")
        elif birth_year:
            base_info_parts.append(f"({birth_year}年-)")
        base_info_parts.append("是中国")
        base_info = "".join(base_info_parts)

        # 处理成就信息
        achievements = result.get('achievements', [])
        achievements_text = ""
        if achievements:
            achievements_list = []
            for item in achievements:
                name = item.get('name', '未知成就')
                year = item.get('year')
                if year:
                    achievements_list.append(f"{name}({year}年)")
                else:
                    achievements_list.append(name)
            achievements_text = "其主要成就包括：" + "；".join(achievements_list) + "。"

        # 处理生平事件
        events = result.get('related_events', [])
        events_text = ""
        if events:
            events_list = []
            for item in events:
                name = item.get('name', '未知事件')
                year = item.get('year')
                if year:
                    events_list.append(f"{name}({year}年)")
                else:
                    events_list.append(name)
            events_text = "其主要生平事件包括：" + "；".join(events_list) + "。"

        # 处理相关实体
        entities = person_data.get('related_entities', [])
        entities_text = ""
        if entities:
            entities_list = []
            for item in entities:
                name = item.get('name', '未知实体')
                entity_type = item.get('type', '未知类型')
                entities_list.append(f"{name}(类型:{entity_type})")
            entities_text = "与之相关的实体包括：" + "、".join(entities_list) + "。"

        # 组装完整段落
        response_parts = [base_info]
        if achievements_text:
            response_parts.append(achievements_text)
        if events_text:
            response_parts.append(events_text)
        if entities_text:
            response_parts.append(entities_text)

        response = " ".join(response_parts).strip()
        response = "。".join([s for s in response.split("。") if s]) + "。"

        return response if response else "未找到相关人员详细信息"

    def assemble_document_search_result(self, search_data: dict) -> str:
        """
        组装文档搜索结果
        """
        documents = search_data.get('result', {}).get('documents', [])
        if not documents:
            return "未找到相关文档"

        # 构建文档列表
        document_list = []
        for doc in documents:
            title = doc.get('title', '未知文档')
            content = doc.get('content', '无内容描述')
            # 提取内容摘要(前50个字符)，处理换行符
            summary = content[:50].replace('\n', ' ') + '...' if len(content) > 50 else content.replace('\n', ' ')
            document_list.append(f"《{title}》：{summary}")

        response = "搜索到以下相关文档：" + "；".join(document_list) + "。"
        return response

    def assemble_achievement_result(self, achievement_data: dict) -> str:
        """
        组装成就搜索结果
        """
        if achievement_data.get('result') is None:
            return achievement_data.get('message', '未找到相关成就')

        # 这里假设achievement_data有特定的结构，根据实际数据调整
        # 由于示例中没有提供完整结构，返回通用消息
        return "找到相关成就信息(具体内容需根据实际数据结构实现)"

    def assemble_entity_result(self, entity_data: dict) -> str:
        """
        组装实体搜索结果
        """
        # 这里假设entity_data有特定的结构，根据实际数据调整
        # 由于示例中没有提供完整结构，返回通用消息
        entities = entity_data.get('result', {}).get('entities', [])
        if not entities:
            return "未找到相关实体"

        entity_list = []
        for entity in entities:
            name = entity.get('name', '未知实体')
            entity_type = entity.get('type', '未知类型')
            entity_list.append(f"{name}(类型:{entity_type})")

        return "找到相关实体：" + "、".join(entity_list) + "。"

    def assemble_inventors_result(self, inventors_data: dict) -> str:
        """
        组装发明家搜索结果
        """
        inventors = inventors_data.get('result', [])
        if not inventors:
            return "未找到相关发明家信息"

        inventor_list = []
        for inventor in inventors:
            name = inventor.get('name', '未知发明家')
            achievement = inventor.get('achievement', '未知成就')
            inventor_list.append(f"{name}：{achievement}")

        response = "找到以下发明家及其成就：" + "；".join(inventor_list) + "。"
        return response

    def assemble_scientists_list_result(self, scientists_data: dict) -> str:
        """
        组装科学家列表搜索结果
        """
        scientists = scientists_data.get('result', [])
        if not scientists:
            return "未找到科学家列表"

        scientist_list = []
        for scientist in scientists:
            name = scientist.get('name', '未知科学家')
            birth_year = scientist.get('birth_year')
            achievements = scientist.get('achievements', [])

            # 构建科学家信息
            scientist_info = f"{name}({birth_year}年生)"
            if achievements:
                achievements_list = []
                for achievement in achievements:
                    achievements_list.append(achievement)
                scientist_info += "，成就：" + "、".join(achievements_list)

            scientist_list.append(scientist_info)

        response = "科学家列表：" + "；".join(scientist_list) + "。"
        return response

    def assemble_person_by_title_result(self, person_by_title_data: dict) -> str:
        """组装按头衔搜索的人物结果"""
        results = person_by_title_data.get('result', [])
        if not results:
            return "未找到相关人物"

        title = person_by_title_data.get('title', '未知头衔')
        person_list = []

        for person in results:
            name = person.get('name', '未知人物')
            year = person.get('year')
            if year:
                person_list.append(f"{name}({year}年)")
            else:
                person_list.append(name)

        response = f"与头衔'{title}'相关的人物：{'; '.join(person_list)}。"
        return response

    def assemble_awards_list_result(self, awards_data: dict) -> str:
        """组装奖项列表搜索结果"""
        awards = awards_data.get('result', [])
        if not awards:
            return "未找到相关奖项"

        award_list = []
        for award in awards:
            award_name = award.get('award_name', '未知奖项')
            award_list.append(award_name)

        response = "找到相关奖项：" + "、".join(award_list) + "。"
        return response

    '''
    获取频率前10的实体
    '''

    def query_frequent_entity(self) -> List[Dict[str, Any]]:

        query = """
                   // 查询所有实体并统计名称出现频率的前10名
                    MATCH (m:Model)-[:HAS_ENTITY]->(n:Entity)
                    WITH n.name AS entity_name, count(*) AS frequency
                    ORDER BY frequency DESC
                    LIMIT 10
                    RETURN entity_name, frequency
                   """

        result = self.db.execute_query(query)
        records = []
        for record in result:
            # 确保所有字段都被正确提取
            record_data = {
                "name": record["entity_name"],
                "frequency": record["frequency"],
            }
            records.append(record_data)

        if not records:
            logger.warning(f"未找到人物")
            return []

        return records

    '''
    获取频率前10实体的关系人返回给前端展示用户点击
    '''

    def query_frequent_relation_old(self, entiy_list: List[str]) -> List[Dict[str, Any]]:

        query = """
          // 查询频率最高的10个实体相关的所有关系
        MATCH (a:Entity)-[r]-(b:Entity)
        WHERE a.name IN $entiy_list
           OR b.name IN $entiy_list
        RETURN 
            a.id AS source_id, 
            a.name AS source_name, 
            type(r) AS relation_type, 
            properties(r) AS relation_properties, 
            b.id AS target_id, 
            b.name AS target_name
        ORDER BY a.name, b.name
            """

        result = self.db.execute_query(query, {"entiy_list": entiy_list})
        records = []
        for record in result:
            # 确保所有字段都被正确提取
            record_data = {
                "source_name": record["source_name"],
                "target_name": record["target_name"],
                "relation_type": record["relation_type"],
            }
            records.append(record_data)

        if not records:
            logger.warning(f"未找到人物关系")
            return []

        return records

    def query_frequent_relation(self, entiy_list: List[str]) -> List[Dict[str, Any]]:

        query = """
         MATCH (a)-[r]-(b)
WHERE type(r) <> 'HAS_ENTITY' AND type(r) <> 'UNKNOWN' AND type(r) <> 'INVOLVED_IN'
RETURN DISTINCT 
    a.name AS source_name, 
    b.name AS target_name, 
    type(r) AS relation_type
            """

        result = self.db.execute_query(query, {"entiy_list": entiy_list})
        records = []
        for record in result:
            # 确保所有字段都被正确提取
            record_data = {
                "source_name": record["source_name"],
                "target_name": record["target_name"],
                "relation_type": record["relation_type"],
            }
            records.append(record_data)

        if not records:
            logger.warning(f"未找到人物关系")
            return []

        return records

    def create_entity_and_relation(self, model_id: str, entity_id: str) -> Tuple[EntityModel, RelationModel]:
        """
        创建默认实体和默认关系。
        """
        entity_data = EntityModel(
            name=DefaultName.DEFAULT_ENTITY_NAME.value,
            properties={
                "source": "default",
            },
            model_id=model_id
        )
        try:
            new_entity = self.create_entity(model_id, entity_data)
        except Exception as e:
            raise ValueError(f"创建实体失败{e}")

        relation_data = RelationModel(
            source_id=entity_id,
            target_id=new_entity.id,
            type=DefaultName.DEFAULT_RELATION_TYPE.value,
            properties={},
            model_id=model_id
        )
        try:
            new_relation = self.create_relation(relation_data)
        except Exception as e:
            raise ValueError(f"创建关系失败{e}")

        return new_entity, new_relation

    def create_default_entities_and_relations(self, model_id: str):
        """
        创建默认实体和默认关系。
        """
        if not model_id:
            raise ValueError("模型 ID 不能为空。")

        default_entities = ('{"data":[{"id":"N1","name":"侯亮平","properties":{"file_type":"image/jpeg",'
                            '"file_name":"test_image.jpg","file_id":"e85ed9ccc37655c29152ed238a6b6099"}},{"id":"N2",'
                            '"name":"李达康","properties":{"file_type":"video/mp4","file_name":"test_video.mp4","file_id":"5d2e88bfe7aa76fea04738d7c4e6238b"}},'
                            '{"id":"N3","name":"祁同伟"},'
                            '{"id":"N4","name":"陈岩石"},{"id":"N5","name":"陆亦可"},{"id":"N6","name":"高育良"},{"id":"N7",'
                            '"name":"沙瑞金"},{"id":"N8","name":"高小琴"},{"id":"N9","name":"高小凤"},{"id":"N10",'
                            '"name":"赵东来"},{"id":"N11","name":"程度"},{"id":"N12","name":"吴惠芬"},{"id":"N13",'
                            '"name":"赵瑞龙"},{"id":"N14","name":"赵立春"},{"id":"N15","name":"陈海"},{"id":"N16",'
                            '"name":"梁璐"},{"id":"N17","name":"刘新建"},{"id":"N18","name":"欧阳菁"},{"id":"N19",'
                            '"name":"吴心怡"},{"id":"N20","name":"蔡成功"},{"id":"N21","name":"丁义珍"}]}')

        default_relations = ('{"data":[{"source_id":"N6","target_id":"N1","type":"师生"},{"source_id":"N6",'
                             '"target_id":"N3","type":"师生"},{"source_id":"N14","target_id":"N6","type":"前领导"},'
                             '{"source_id":"N14","target_id":"N13","type":"父子"},{"source_id":"N14","target_id":"N17",'
                             '"type":"前部队下属"},{"source_id":"N2","target_id":"N14","type":"前任秘书"},{"source_id":"N3",'
                             '"target_id":"N8","type":"情人"},{"source_id":"N4","target_id":"N15","type":"父子"},'
                             '{"source_id":"N5","target_id":"N15","type":"属下"},{"source_id":"N7","target_id":"N4",'
                             '"type":"故人"},{"source_id":"N3","target_id":"N15","type":"师哥"},{"source_id":"N3",'
                             '"target_id":"N1","type":"师哥"},{"source_id":"N1","target_id":"N15","type":"同学，生死朋友"},'
                             '{"source_id":"N6","target_id":"N12","type":"夫妻"},{"source_id":"N15","target_id":"N10",'
                             '"type":"朋友"},{"source_id":"N8","target_id":"N9","type":"双胞胎"},{"source_id":"N10",'
                             '"target_id":"N5","type":"爱慕"},{"source_id":"N3","target_id":"N11","type":"领导"},'
                             '{"source_id":"N6","target_id":"N9","type":"情人"},{"source_id":"N13","target_id":"N3",'
                             '"type":"勾结"},{"source_id":"N2","target_id":"N10","type":"领导"},{"source_id":"N13",'
                             '"target_id":"N11","type":"领导"},{"source_id":"N7","target_id":"N2","type":"领导"},'
                             '{"source_id":"N7","target_id":"N6","type":"领导"},{"source_id":"N3","target_id":"N16",'
                             '"type":"夫妻"},{"source_id":"N12","target_id":"N16","type":"朋友"},{"source_id":"N2",'
                             '"target_id":"N18","type":"夫妻"},{"source_id":"N13","target_id":"N17","type":"洗钱工具"},'
                             '{"source_id":"N13","target_id":"N8","type":"勾结，腐化"},{"source_id":"N13",'
                             '"target_id":"N9","type":"腐化"},{"source_id":"N19","target_id":"N5","type":"母女"},'
                             '{"source_id":"N19","target_id":"N12","type":"姐妹"},{"source_id":"N20","target_id":"N1",'
                             '"type":"发小"},{"source_id":"N20","target_id":"N18","type":"举报"},{"source_id":"N18",'
                             '"target_id":"N17","type":"举报"},{"source_id":"N17","target_id":"N13","type":"举报"},'
                             '{"source_id":"N2","target_id":"N21","type":"领导"},{"source_id":"N8","target_id":"N21",'
                             '"type":"策划出逃"},{"source_id":"N3","target_id":"N21","type":"勾结"},{"source_id":"N13",'
                             '"target_id":"N21","type":"勾结"}]}')

        # 1. 解析 JSON 数据
        entities_data = json.loads(default_entities)
        relations_data = json.loads(default_relations)

        # 2. 生成 UUID 映射
        id_mapping = {}
        for node in entities_data['data']:
            old_id = node['id']
            new_uuid = str(uuid.uuid4())  # 生成一个新的UUID
            id_mapping[old_id] = new_uuid
            node['id'] = new_uuid  # 直接更新节点中的id
            node['model_id'] = model_id

        # 3. 更新关系 ID
        for relationship in relations_data['data']:
            source_id = relationship['source_id']
            target_id = relationship['target_id']
            relationship['model_id'] = model_id

            relationship['source_id'] = id_mapping.get(source_id, source_id)
            relationship['target_id'] = id_mapping.get(target_id, target_id)

        entities = [EntityModel(**item) for item in entities_data['data']]
        relations = [RelationModel(**item) for item in relations_data['data']]
        try:
            entities_result = self.create_bulk_entities(model_id, entities)
            relations_result = self.create_bulk_relations(relations)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"创建默认的实体和关系失败：{e}")

        return [entities_result, relations_result]

    def graph_algorithm_pagerank(self, model_id: str, damping_factor: float = 0.85,
                                 max_iterations: int = 20, write_property_name: str = "page_rank",
                                 exponent_for_scaling: float = 3.0):
        """
        pagerank 算法
        Args:
            self: 包含 self.db 对象的实例，且具有 update_entity 方法。
            model_id (str): 模型的 ID (对应 Model 节点的 'id' 属性值)。
            damping_factor (float): PageRank 算法的阻尼系数。
            max_iterations (int): PageRank 算法的最大迭代次数。
            write_property_name (str): PageRank 分数要写入到节点上的属性名。
            exponent_for_scaling (float): 用于 PageRank 分数非线性缩放的指数。
                                          大于 1 的值会增加高分之间的差异。
        """
        # 生成一个有效的图投影名称，替换 model_id 中的非字母数字字符
        graph_project_name = "pagerank_" + model_id
        processed_pagerank_scores: Dict[str, float] = {}

        try:
            # 1. 创建或获取图投影
            node_projection_cypher = """
                    MATCH (m:Model {id: $model_id_param})-[:HAS_ENTITY]->(e:Entity)
                    RETURN id(e) AS id
                    """
            relationship_projection_cypher = """
                    MATCH (s:Entity)-[r]->(t:Entity)
                    WHERE EXISTS((:Model {id: $model_id_param})-[:HAS_ENTITY]->(s))
                      AND EXISTS((:Model {id: $model_id_param})-[:HAS_ENTITY]->(t))
                    RETURN id(s) AS source, id(t) AS target, type(r) AS type
                    """

            project_params = {
                "graph_name": graph_project_name,
                "node_projection_cypher": node_projection_cypher,
                "relationship_projection_cypher": relationship_projection_cypher,
                "model_id_value": model_id
            }

            gds_project_query_string = f"""
                        CALL gds.graph.project.cypher(
                            $graph_name,
                            $node_projection_cypher,
                            $relationship_projection_cypher,
                            {{
                                parameters: {{model_id_param: $model_id_value}}
                            }}
                        )
                        """
            self.db.execute_query(gds_project_query_string, project_params)

            logger.info(f"图投影 '{graph_project_name}' 已为模型 '{model_id}' 下的实体创建/获取。")

            # 2. 运行 PageRank 算法并流式传输结果
            pagerank_stream_query = f"""
                    CALL gds.pageRank.stream(
                        $graph_name,
                        {{
                            maxIterations: $max_iterations,
                            dampingFactor: $damping_factor
                        }}
                    )
                    YIELD nodeId, score
                    RETURN nodeId, score
                    """

            stream_params = {
                "graph_name": graph_project_name,
                "max_iterations": max_iterations,
                "damping_factor": damping_factor
            }

            stream_results = self.db.execute_query(pagerank_stream_query, stream_params)

            pagerank_scores = {}
            if stream_results:
                logger.info(
                    f"PageRank 算法在模型 '{model_id}' 的投影上执行完毕。开始使用 update_entity 写入结果到数据库...")

                # 3. 迭代结果并使用 update_entity 方法将 PageRank 分数存储到实体节点
                for record in stream_results:
                    node_id_neo4j = record["nodeId"]  # GDS 返回的 nodeId 即为 Neo4j 内部的节点ID
                    score = record["score"]

                    # 获取实体的业务ID (现在我们假设它就是 'id' 属性)
                    get_business_id_query = f"""
                            MATCH (e:Entity)
                            WHERE id(e) = $node_id_neo4j
                            RETURN e.id AS business_id
                            """
                    business_id_result = self.db.execute_query(get_business_id_query, {"node_id_neo4j": node_id_neo4j})

                    if business_id_result and business_id_result[0]:
                        entity_business_id = business_id_result[0]["business_id"]
                        pagerank_scores[entity_business_id] = score
                    else:
                        logger.warning(f"无法为 Neo4j 节点 ID {node_id_neo4j} 获取业务 ID ('id' 属性)，跳过更新。")
            else:
                logger.info(f"PageRank 算法执行完毕，但没有获取到任何结果。")

            # --- PageRank 分数后期处理：指数缩放并归一化到百分制 ---
            if pagerank_scores:
                # 提取所有原始分数，用于找到最大最小值
                original_scores_values = list(pagerank_scores.values())

                # 避免所有分数都为零（如果PageRank结果为空或者所有节点无入度）
                if all(s == 0 for s in original_scores_values):
                    # 如果所有分数都是0，则全部映射到0，或者给一个默认值
                    processed_pagerank_scores = {k: 0.0 for k in pagerank_scores.keys()}
                else:
                    # 1. 指数缩放
                    # 对每个分数进行指数运算，确保即使原始分数很小也能保持相对大小
                    # 使用 math.pow 兼容性更好
                    scaled_scores: Dict[str, float] = {
                        k: math.pow(v, exponent_for_scaling)
                        for k, v in pagerank_scores.items()
                    }

                    # 找到指数缩放后的最大值和最小值
                    min_scaled = min(scaled_scores.values())
                    max_scaled = max(scaled_scores.values())

                    # 2. 归一化到 0-10 范围 (百分制)
                    target_min_value = 0.0  # 目标范围最小值
                    target_max_value = 10.0  # 目标范围最大值

                    if max_scaled == min_scaled:
                        # 如果所有分数相同，则映射到目标范围的中间值
                        processed_pagerank_scores = {k: (target_min_value + target_max_value) / 2 for k in
                                                     scaled_scores.keys()}
                    else:
                        for business_id, scaled_score in scaled_scores.items():
                            # 归一化公式：NewValue = (OldValue - OldMin) / (OldMax - OldMin) * (NewMax - NewMin) + NewMin
                            normalized_score = target_min_value + (
                                    (scaled_score - min_scaled) / (max_scaled - min_scaled)) * (
                                                       target_max_value - target_min_value)
                            processed_pagerank_scores[business_id] = round(normalized_score, 2)

                logger.info(f"PageRank 分数已成功进行指数缩放并归一化到百分制。")

                # 3. 将处理后的分数写入数据库 (或直接返回给调用者)
                for entity_business_id, final_score in processed_pagerank_scores.items():
                    update_data = {
                        "properties": {
                            write_property_name: final_score
                        }
                    }
                    try:
                        self.update_entity(entity_business_id, update_data)
                    except Exception as update_e:
                        logger.warning(
                            f"调用 update_entity 更新实体 '{entity_business_id}' (百分制PageRank) 时发生错误: {update_e}")

        except Exception as e:
            logger.error(f"执行 PageRank 算法时发生错误: {e}", exc_info=True)  # exc_info=True 打印完整的堆栈信息
            return {"message": f"PageRank 算法执行完毕，但没有获取到任何结果。"}
        finally:
            # 4. 删除图投影（重要，释放 GDS 内存）
            drop_graph_query = """
                    CALL gds.graph.drop($graph_name) YIELD graphName
                    """
            drop_params = {"graph_name": graph_project_name}

            try:
                self.db.execute_query(drop_graph_query, drop_params)
                logger.info(f"图投影 '{graph_project_name}' 已删除。")
            except Exception as e:
                logger.warning(f"删除图投影时发生错误 (可能它不存在或已被删除): {e}")

        if processed_pagerank_scores:
            return {"message": "PageRank 算法执行完毕",
                    "data": processed_pagerank_scores}
        else:
            return {"message": "PageRank 算法执行完毕，但没有获取到任何结果。"}

    def graph_algorithm_community_detection_louvain(
            self,
            model_id: str,
            write_property_name: str = "community_id"
    ):
        """ 社区发现算法 Louvain """
        # 生成一个有效的图投影名称，替换 model_id 中的非字母数字字符
        graph_project_name = "louvain_" + model_id
        community_scores = {}

        try:
            # 1. 创建或获取图投影 (与 PageRank 相同)
            node_projection_cypher = """
                    MATCH (m:Model {id: $model_id_param})-[:HAS_ENTITY]->(e:Entity)
                    RETURN id(e) AS id
                    """
            relationship_projection_cypher = """
                    MATCH (s:Entity)-[r]->(t:Entity)
                    WHERE EXISTS((:Model {id: $model_id_param})-[:HAS_ENTITY]->(s))
                      AND EXISTS((:Model {id: $model_id_param})-[:HAS_ENTITY]->(t))
                    RETURN id(s) AS source, id(t) AS target, type(r) AS type
                    """

            project_params = {
                "graph_name": graph_project_name,
                "node_projection_cypher": node_projection_cypher,
                "relationship_projection_cypher": relationship_projection_cypher,
                "model_id_value": model_id
            }

            gds_project_query_string = f"""
                        CALL gds.graph.project.cypher(
                            $graph_name,
                            $node_projection_cypher,
                            $relationship_projection_cypher,
                            {{
                                parameters: {{model_id_param: $model_id_value}}
                            }}
                        )
                        """
            self.db.execute_query(gds_project_query_string, project_params)
            logger.info(f"图投影 '{graph_project_name}' 已为模型 '{model_id}' 下的实体创建/获取。")

            # 2. 运行 Louvain 社区检测算法并流式传输结果
            louvain_stream_query = f"""
                    CALL gds.louvain.stream(
                        $graph_name
                    )
                    YIELD nodeId, communityId
                    RETURN nodeId, communityId
                    """

            stream_params = {
                "graph_name": graph_project_name
            }

            stream_results = self.db.execute_query(louvain_stream_query, stream_params)

            community_scores = {}
            if stream_results:
                # 批量获取业务ID
                node_ids = [rec["nodeId"] for rec in stream_results]
                id_query = """
                            UNWIND $node_ids AS nodeId
                            MATCH (e:Entity)
                            WHERE id(e) = nodeId
                            RETURN nodeId, e.id AS business_id
                            """
                id_mapping = {
                    rec["nodeId"]: rec["business_id"]
                    for rec in self.db.execute_query(id_query, {"node_ids": node_ids})
                }

                # 批量更新节点
                for record in stream_results:
                    node_id = record["nodeId"]
                    community_id = record["communityId"]

                    if business_id := id_mapping.get(node_id):
                        update_data = {"properties": {write_property_name: community_id}}
                        try:
                            self.update_entity(business_id, update_data)
                            community_scores[business_id] = community_id
                        except Exception as e:
                            logger.warning(f"更新失败 {business_id}: {e}")
                    else:
                        logger.warning(f"找不到业务ID: {node_id}")

                logger.info(f"更新了 {len(community_scores)} 个实体的社区ID")
            else:
                logger.info(f"Louvain 算法执行完毕，但没有获取到任何结果。")

        except Exception as e:
            logger.error(f"执行 Louvain 社区检测算法时发生错误: {e}", exc_info=True)
            return {"message": f"社区检测算法执行完毕，但没有找到社区ID"}
        finally:
            # 4. 删除图投影（重要）
            drop_graph_query = """
                    CALL gds.graph.drop($graph_name) YIELD graphName
                    """
            drop_params = {"graph_name": graph_project_name}
            try:
                self.db.execute_query(drop_graph_query, drop_params)
                logger.info(f"图投影 '{graph_project_name}' 已删除。")
            except Exception as e:
                logger.warning(f"删除图投影时发生错误 (可能它不存在或已被删除): {e}")

        if not community_scores:
            return {"message": "社区检测算法执行完毕，但没有找到社区ID"}
        return {"message": "社区检测算法执行完毕", "data": community_scores}

    def graph_algorithm_shortest_path(
            self,
            model_id: str,
            start_entity_id: str,
            end_entity_id: Optional[str] = None,
            relationship_type: Optional[str] = None,
            cost_property: Optional[str] = None,
            write_shortest_path_property_name: Optional[str] = "shortest_paths",
    ):
        graph_project_name = "dijkstra_" + model_id
        shortest_paths_data = {}

        try:
            # 1. 创建或获取图投影
            node_projection_cypher = """
                    MATCH (m:Model {id: $model_id_param})-[:HAS_ENTITY]->(e:Entity)
                    RETURN id(e) AS id
                    """

            relationship_projection_cypher = """
                    MATCH (s:Entity)-[r]->(t:Entity)
                    WHERE EXISTS((:Model {id: $model_id_param})-[:HAS_ENTITY]->(s))
                      AND EXISTS((:Model {id: $model_id_param})-[:HAS_ENTITY]->(t))
                    """
            if relationship_type:
                relationship_projection_cypher += f" AND type(r) = '{relationship_type}'"

            relationship_projection_cypher += " RETURN id(s) AS source, id(t) AS target, type(r) AS type"
            if cost_property:
                relationship_projection_cypher += f", toFloat(r.{cost_property}) AS cost"
            else:
                relationship_projection_cypher += ", 1.0 AS cost"

            project_params = {
                "graph_name": graph_project_name,
                "node_projection_cypher": node_projection_cypher,
                "relationship_projection_cypher": relationship_projection_cypher,
                "model_id_value": model_id
            }

            gds_project_query_string = f"""
                        CALL gds.graph.project.cypher(
                            $graph_name,
                            $node_projection_cypher,
                            $relationship_projection_cypher,
                            {{
                                parameters: {{model_id_param: $model_id_value}}
                            }}
                        )
                        """
            self.db.execute_query(gds_project_query_string, project_params)
            logger.info(f"图投影 '{graph_project_name}' 已为模型 '{model_id}' 下的实体创建/获取。")

            # 获取起始实体的 Neo4j 内部 ID
            get_start_node_id_query = f"""
                    MATCH (m:Model {{id: $model_id_param}})-[:HAS_ENTITY]->(startNode:Entity {{id: $start_entity_id}})
                    RETURN id(startNode) AS start_node_neo4j_id
                    """
            start_node_id_result = self.db.execute_query(get_start_node_id_query, {
                "model_id_param": model_id,
                "start_entity_id": start_entity_id
            })

            if not start_node_id_result or not start_node_id_result[0]:
                logger.error(f"未找到起始实体 '{start_entity_id}' 或其不属于模型 '{model_id}'。")
                return None

            start_node_neo4j_id = start_node_id_result[0]["start_node_neo4j_id"]
            logger.info(f"起始实体 '{start_entity_id}' 的 Neo4j 内部 ID 是: {start_node_neo4j_id}")

            shortest_paths_data: Dict[str, List[str]] = {}  # 存储结果：目标实体ID -> 路径节点ID列表

            if end_entity_id:
                # 如果指定了 end_entity_id，则计算到这一个目标的路径
                get_end_node_id_query = f"""
                        MATCH (m:Model {{id: $model_id_param}})-[:HAS_ENTITY]->(endNode:Entity {{id: $end_entity_id}})
                        RETURN id(endNode) AS end_node_neo4j_id
                        """
                end_node_id_result = self.db.execute_query(get_end_node_id_query, {
                    "model_id_param": model_id,
                    "end_entity_id": end_entity_id
                })

                if not end_node_id_result or not end_node_id_result[0]:
                    logger.error(f"未找到目标实体 '{end_entity_id}' 或其不属于模型 '{model_id}'。")
                    return {"message": f"未找到目标实体 '{end_entity_id}' 或其不属于模型 '{model_id}'。"}

                end_node_neo4j_id = end_node_id_result[0]["end_node_neo4j_id"]
                logger.info(f"目标实体 '{end_entity_id}' 的 Neo4j 内部 ID 是: {end_node_neo4j_id}")

                # 使用 gds.allShortestPaths.delta.stream 针对特定目标进行筛选
                shortest_path_query = f"""
                        CALL gds.allShortestPaths.delta.stream(
                            $graph_name,
                            {{
                                sourceNode: $start_node_neo4j_id,
                                relationshipWeightProperty: 'cost'
                            }}
                        )
                        YIELD sourceNode, targetNode, path
                        WHERE targetNode = $end_node_neo4j_id
                        RETURN [node IN nodes(path) | node.id] AS path_entity_ids // 直接返回路径上所有节点的业务ID
                        """
                stream_params = {
                    "graph_name": graph_project_name,
                    "start_node_neo4j_id": start_node_neo4j_id,
                    "end_node_neo4j_id": end_node_neo4j_id
                }

                stream_results = self.db.execute_query(shortest_path_query, stream_params)

                if stream_results:
                    record = stream_results[0]  # 对于单目标，我们只取第一条结果
                    path_entity_ids = record["path_entity_ids"]  # 直接获取到的是业务ID列表

                    if path_entity_ids and len(path_entity_ids) >= 2:  # 路径至少包含起点和终点
                        final_target_entity_id = path_entity_ids[-1]  # 路径的最后一个就是目标实体ID
                        shortest_paths_data[final_target_entity_id] = path_entity_ids

                        if write_shortest_path_property_name:
                            # --- 方案二：读取现有属性，更新，再写回 ---
                            try:
                                # 先读取目标实体，获取其所有属性
                                target_entity_model = self.get_entity(final_target_entity_id)
                                existing_shortest_paths = target_entity_model.properties.get(
                                    write_shortest_path_property_name, {}
                                ).copy()  # 确保是可修改的副本

                                # 更新当前起始点的路径
                                existing_shortest_paths[start_entity_id] = path_entity_ids

                                update_data = {
                                    "properties": {
                                        write_shortest_path_property_name: existing_shortest_paths
                                    }
                                }
                                self.update_entity(final_target_entity_id, update_data)
                            except HTTPException as update_e:
                                logger.warning(
                                    f"更新实体 '{final_target_entity_id}' 的最短路径时发生错误: {update_e.detail}")
                            except Exception as update_e:
                                logger.warning(
                                    f"更新实体 '{final_target_entity_id}' 的最短路径时发生未知错误: {update_e}")

                            logger.info(f"找到从 '{start_entity_id}' 到 '{end_entity_id}' 的最短路径，并已存储。")
                        else:
                            logger.info(
                                f"未指定写入属性名，路径未存储，但已找到从 '{start_entity_id}' 到 '{end_entity_id}' 的有效路径。")
                    else:
                        logger.info(f"未找到从 '{start_entity_id}' 到 '{end_entity_id}' 的有效路径。")
                else:
                    logger.info(f"未找到从 '{start_entity_id}' 到 '{end_entity_id}' 的最短路径。")

            else:
                # 否则，计算到所有可达节点的最短路径
                shortest_path_query = f"""
                                CALL gds.allShortestPaths.delta.stream(
                                    $graph_name,
                                    {{
                                        sourceNode: $start_node_neo4j_id,
                                        relationshipWeightProperty: 'cost'
                                    }}
                                )
                                YIELD sourceNode, targetNode, path
                                WHERE sourceNode <> targetNode
                                // 直接通过匹配节点来获取其业务ID，避免使用 gds.util.asNode()
                                MATCH (target_node:Entity) WHERE id(target_node) = targetNode
                                RETURN [node IN nodes(path) | node.id] AS path_entity_ids, target_node.id AS target_entity_business_id
                                """
                stream_params = {
                    "graph_name": graph_project_name,
                    "start_node_neo4j_id": start_node_neo4j_id
                }

                stream_results = self.db.execute_query(shortest_path_query, stream_params)

                if stream_results:
                    logging.info(
                        f"gds.allShortestPaths.delta.stream 算法从实体 '{start_entity_id}' 开始执行完毕。开始处理结果...")

                    for record in stream_results:
                        path_entity_ids = record["path_entity_ids"]
                        final_target_entity_id = record["target_entity_business_id"]  # 直接获取目标实体的业务ID

                        if path_entity_ids and len(path_entity_ids) >= 2:
                            shortest_paths_data[final_target_entity_id] = path_entity_ids

                            if write_shortest_path_property_name:
                                try:
                                    target_entity_model = self.get_entity(final_target_entity_id)
                                    existing_shortest_paths = target_entity_model.properties.get(
                                        write_shortest_path_property_name, {}
                                    ).copy()

                                    existing_shortest_paths[start_entity_id] = path_entity_ids

                                    update_data = {
                                        "properties": {
                                            write_shortest_path_property_name: existing_shortest_paths
                                        }
                                    }
                                    self.update_entity(final_target_entity_id, update_data)
                                except HTTPException as update_e:
                                    logging.warning(
                                        f"更新实体 '{final_target_entity_id}' 的最短路径时发生错误: {update_e.detail}")
                                except Exception as update_e:
                                    logging.warning(
                                        f"更新实体 '{final_target_entity_id}' 的最短路径时发生未知错误: {update_e}")
                        else:
                            logging.warning(f"从 {start_entity_id} 到 {final_target_entity_id} 的路径未找到或无效。")
                else:
                    logging.info(
                        f"gds.allShortestPaths.delta.stream 算法执行完毕，但没有找到从 '{start_entity_id}' 到任何其他实体的路径。")

        except Exception as e:
            logger.error(f"执行最短路径算法时发生错误: {e}", exc_info=True)
            return {"message": f"未找到最短路径。"}
        finally:
            # 4. 删除图投影
            drop_graph_query = """
                            CALL gds.graph.drop($graph_name) YIELD graphName
                            """
            drop_params = {"graph_name": graph_project_name}
            try:
                self.db.execute_query(drop_graph_query, drop_params)
                logger.info(f"图投影 '{graph_project_name}' 已删除。")
            except Exception as e:
                logger.warning(f"删除图投影时发生错误 (可能它不存在或已被删除): {e}")

        if not shortest_paths_data:
            return {"message": f"未找到最短路径。"}
        return {"message": f"计算最短路径成功。", "data": shortest_paths_data}


neo4jController = Neo4jController()
knowledgeGraphController = KnowledgeGraphController(neo4jController)

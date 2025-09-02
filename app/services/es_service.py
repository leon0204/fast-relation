from elasticsearch import Elasticsearch
import logging
from elasticsearch import helpers
from app.settings import settings

logger = logging.getLogger(__name__)


class ElasticsearchService:
    def __init__(self):
        # self.es = Elasticsearch("124.222.117.99", port=9200, http_auth=("elastic", "123456aL!"), timeout=10000)
        self.es = Elasticsearch(f"http://{settings.ES_HOSTS}",http_auth=(settings.ES_USER, settings.ES_PASSWORD) if settings.ES_USER else None, port=9200, timeout=60)

    def close(self):
        """关闭Elasticsearch客户端连接"""
        self.es.close()
        logger.info("Elasticsearch客户端连接已关闭")

    async def create_document(self, index: str, document: dict):
        """
        创建单个文档

        :param index: 索引名称
        :param document: 要插入的文档（字典形式）
        :return: 插入结果
        """
        try:
            response = self.es.index(index=index, document=document)
            logger.info(f"成功创建文档，ID: {response['_id']}")
            return response
        except Exception as e:
            logger.error(f"创建文档失败: {str(e)}")
            raise

    def bulk_create_documents_old(self, index: str, documents: list):
        """
        批量创建文档

        :param index: 索引名称
        :param documents: 要插入的文档列表（每个文档为字典）
        :return: 批量插入结果
        """
        try:
            # 使用helpers.bulk进行批量插入
            actions = [
                {
                    "_index": index,
                    "_source": doc
                }
                for doc in documents
            ]
            success, failed = helpers.bulk(self.es, actions)
            logger.info(f"批量创建文档成功: {success} 条，失败: {len(failed)} 条")
            if failed:
                logger.error(f"失败的文档: {failed}")
            return {"success": success, "failed": failed}
        except Exception as e:
            logger.error(f"批量创建文档失败: {str(e)}")
            raise

    def bulk_create_documents(self, index: str, documents: list):
        """
        批量创建文档（插入前检查 name、properties.text 和 properties.source 是否已存在）

        :param index: 索引名称
        :param documents: 要插入的文档列表（每个文档为字典）
        :return: 批量插入结果
        """
        try:
            # 收集所有需要检查的文档特征
            doc_features = []
            for doc in documents:
                name = doc.get("name")
                text = doc.get("properties", {}).get("text")
                source = doc.get("properties", {}).get("source")

                if name and text and source:
                    doc_features.append((name, text, source))

            # 如果没有需要检查的文档，直接返回
            if not doc_features:
                logger.info("没有有效的文档需要检查")
                return {"success": 0, "failed": 0}

            # 构建查询条件
            should_conditions = []
            for name, text, source in doc_features:
                should_conditions.append({
                    "bool": {
                        "must": [
                            {"term": {"name.keyword": name}},
                            {"term": {"properties.text.keyword": text}},
                            {"term": {"properties.source.keyword": source}}
                        ]
                    }
                })

            query = {
                "query": {
                    "bool": {
                        "should": should_conditions,
                        "minimum_should_match": 1
                    }
                },
                "_source": ["name", "properties.text", "properties.source"],
                "size": len(doc_features)  # 只需要匹配我们检查的数量
            }

            # 执行查询获取已存在的文档
            existing_docs = set()
            try:
                result = self.es.search(index=index, body=query)
                for hit in result["hits"]["hits"]:
                    src = hit["_source"]
                    key = (src.get("name"),
                           src.get("properties", {}).get("text"),
                           src.get("properties", {}).get("source"))
                    if all(key):  # 确保三个字段都有值
                        existing_docs.add(key)
            except Exception as e:
                logger.warning(f"查询已存在文档时出错，将插入所有文档: {str(e)}")
                existing_docs = set()

            # 过滤掉已存在的文档
            actions = []
            for doc in documents:
                name = doc.get("name")
                text = doc.get("properties", {}).get("text")
                source = doc.get("properties", {}).get("source")

                if not all([name, text, source]) or (name, text, source) not in existing_docs:
                    actions.append({
                        "_op_type": "create",  # 使用create操作确保不会覆盖已有文档
                        "_index": index,
                        "_source": doc
                    })

            # 执行批量插入
            if actions:
                success, failed = helpers.bulk(self.es, actions)
                logger.info(f"批量创建文档成功: {success} 条，失败: {len(failed)} 条")
                if failed:
                    logger.error(f"失败的文档: {failed}")
                return {"success": success, "failed": failed}
            else:
                logger.info("所有文档已存在，无需插入")
                return {"success": 0, "failed": 0}

        except Exception as e:
            logger.error(f"批量创建文档失败: {str(e)}")
            raise

    async def search_documents(self, index: str, query: dict):
        """
        查询文档

        :param index: 索引名称
        :param query: 查询DSL（字典形式）
        :return: 查询结果
        """
        try:
            response = self.es.search(index=index, body=query)
            logger.info(f"查询到 {response['hits']['total']['value']} 条文档")
            return response['hits']['hits']
        except Exception as e:
            logger.error(f"查询文档失败: {str(e)}")
            raise

    def index_exists(self, index: str) -> bool:
        """
        检查索引是否存在

        :param index: 索引名称
        :return: 如果索引存在返回True，否则返回False
        """
        try:
            exists = self.es.indices.exists(index=index)
            logger.debug(f"索引 {index} 存在状态: {exists}")
            return exists
        except Exception as e:
            logger.error(f"检查索引 {index} 是否存在失败: {str(e)}")
            raise

    async def search_documents_total(self, index: str, query: dict):
        """
        查询文档

        :param index: 索引名称
        :param query: 查询DSL（字典形式）
        :return: 查询结果
        """
        try:
            response = self.es.search(index=index, body=query)
            logger.info(f"查询到 {response['hits']['total']['value']} 条文档")

            return {
                "hits": response['hits']['hits'],
                "total": response['hits']['total']['value']
            }
        except Exception as e:
            logger.error(f"查询文档失败: {str(e)}")
            raise

    def bulk_full_update_documents(self, documents, index):
        """
        使用update API实现全量更新（保留文档版本等元数据）
        """
        actions = [
            {
                "_op_type": "update",
                "_index": index,
                "_id": doc["_id"],
                "doc": doc["_source"]  # 注意这里使用全量文档内容
            }
            for doc in documents
        ]

        try:
            success, failed = helpers.bulk(self.es, actions)
            print(f"成功更新 {success} 个文档，失败 {len(failed)} 个")
            return success, failed
        except Exception as e:
            print(f"全量更新失败: {str(e)}")
            raise

    def bulk_full_update_relations(self, documents, index):
        """
        使用update API实现全量更新（保留文档版本等元数据）
        """
        actions = [
            {
                "_op_type": "update",
                "_index": index,
                "_id": doc["_id"],
                "doc": {
                    "relation": doc["relation"]  # 只更新relation字段
                }
            }
            for doc in documents
        ]

        try:
            success, failed = helpers.bulk(self.es, actions)
            print(f"成功更新 {success} 个文档，失败 {len(failed)} 个")
            return success, failed
        except Exception as e:
            print(f"全量更新失败: {str(e)}")
            raise

    def delete_merge(self, keep_id: str, id_list: list) -> dict:
        """
        消岐合并操作：保留指定ID，消岐列表中其他所有ID

        :param keep_id: 需要保留的实体ID
        :param id_list: 需要处理的ID列表（包含待消岐ID和保留ID）
        :return: 操作结果 {
            "success": bool,
            "message": str,
            "deleted_ids": list,
            "kept_id": str
        }
        """
        # 1. 检查keep_id是否在列表中
        if keep_id not in id_list:
            return {
                "success": False,
                "message": f"目标ID {keep_id} 不在提供的ID列表中",
                "deleted_ids": [],
                "kept_id": ""
            }

        # 2. 过滤出需要消岐的ID（排除keep_id）
        ids_to_delete = [doc_id for doc_id in id_list if doc_id != keep_id]

        if not ids_to_delete:
            return {
                "success": True,
                "message": "无需消岐，列表中只有要保留的ID",
                "deleted_ids": [],
                "kept_id": keep_id
            }

        # 3. 执行批量消岐
        try:
            # 构建批量消岐请求
            delete_actions = [
                {"_op_type": "delete", "_index": "entity", "_id": doc_id}
                for doc_id in ids_to_delete
            ]

            # 执行批量操作
            success_count, errors = helpers.bulk(self.es, delete_actions)

            # 处理结果
            if len(errors) > 0:
                return {
                    "success": False,
                    "message": f"部分消岐失败，成功消岐 {success_count} 个",
                    "deleted_ids": ids_to_delete,
                    "kept_id": keep_id,
                    "errors": errors
                }

            return {
                "success": True,
                "message": f"成功消岐 {len(ids_to_delete)} 个文档",
                "deleted_ids": ids_to_delete,
                "kept_id": keep_id
            }

        except Exception as e:
            return {
                "success": False,
                "message": f"消岐操作异常: {str(e)}",
                "deleted_ids": [],
                "kept_id": keep_id
            }
es_service = ElasticsearchService()

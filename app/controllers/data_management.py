import hashlib
import base64
import io
import json
import os
import re
import uuid
from urllib.parse import quote
from datetime import datetime
import logging
from typing import List, Dict, Any

from elasticsearch import helpers, AsyncElasticsearch
from elasticsearch.helpers import async_bulk
from fastapi import Depends, HTTPException, UploadFile, File
from fastapi.responses import JSONResponse, StreamingResponse
from pydantic import ValidationError
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from aiokafka import AIOKafkaConsumer

from app.utils.database import get_es_session
from app.schemas.data_management import (DataSourceRequest, DataSourceModel, DataManagementItem,
                                         DataManagementListResponse, DamengFieldsResponse)

logger = logging.getLogger(__name__)


class DataManagementController:
    def __init__(self, es_session: AsyncElasticsearch = Depends(get_es_session)):
        self.DEFAULT_INDEX_NAME = "unknown_data"
        self.DEFAULT_REMOTE_INDEX_NAME = "remote_data"

        self.es_session = es_session

    @staticmethod
    def generate_id(content_str: str) -> str:
        return hashlib.md5(content_str.encode("utf-8")).hexdigest()

    @staticmethod
    def prepare_doc(self, data):
        # 确保 raw_data 始终是一个字典
        if isinstance(data, dict):
            content_str = json.dumps(data, ensure_ascii=False)
            raw_data = data
        elif isinstance(data, str):
            try:
                parsed = json.loads(data)
                content_str = json.dumps(parsed, ensure_ascii=False)
                raw_data = parsed if isinstance(parsed, dict) else {"value": parsed}
            except Exception:
                content_str = data
                raw_data = {"value": data}
        else:
            if isinstance(data, bytes):
                content_str = base64.b64encode(data).decode()
                raw_data = {"value": content_str}
            else:
                content_str = str(data)
                raw_data = {"value": content_str}

        # 确保 raw_data 是一个字典
        if not isinstance(raw_data, dict):
            raw_data = {"value": raw_data}

        # 确保 content 是字符串
        if not isinstance(content_str, str):
            content_str = json.dumps(content_str, ensure_ascii=False)

        doc_id = self.generate_id(content_str)
        return {
            "_index": self.DEFAULT_INDEX_NAME,
            "_id": doc_id,
            "_source": {
                "content": content_str,
                "raw": raw_data,
                # "timestamp": datetime.datetime.utcnow().isoformat()
            }
        }

    async def upload_file(self, file: UploadFile = File(...)):
        content = await file.read()

        actions = []
        try:
            # 尝试解析为JSON
            try:
                data = json.loads(content)
                if isinstance(data, list):
                    actions = [self.prepare_doc(item) for item in data]
                else:
                    actions = [self.prepare_doc(data)]
            except json.JSONDecodeError:
                # 如果不是JSON，按行处理
                content_str = content.decode('utf-8')
                for line in content_str.splitlines():
                    if not line.strip():
                        continue
                    try:
                        data = json.loads(line)
                    except json.JSONDecodeError:
                        data = line
                    actions.append(self.prepare_doc(data))

            # 批量导入前先检查索引是否存在
            if not self.es_session.indices.exists(index=self.DEFAULT_INDEX_NAME):
                self.es_session.indices.create(index=self.DEFAULT_INDEX_NAME)

            # 执行批量导入
            if actions:
                success, failed = 0, 0
                try:
                    # 使用更详细的错误处理
                    async for ok, item in helpers.async_streaming_bulk(self.es_session, actions, raise_on_error=False):
                        if not ok:
                            print(f"Error indexing document: {item}")
                            failed += 1
                        else:
                            success += 1

                    # 刷新索引
                    self.es_session.indices.refresh(index=self.DEFAULT_INDEX_NAME)

                    return {
                        "message": f"文件处理完成",
                        "details": {
                            "total": len(actions),
                            "success": success,
                            "failed": failed
                        }
                    }

                except Exception as e:
                    raise HTTPException(
                        status_code=500,
                        detail={
                            "message": "批量导入数据时出错",
                            "error": str(e),
                            "processed": len(actions)
                        }
                    )
            else:
                return {"message": "未找到可处理的数据"}

        except Exception as e:
            raise HTTPException(
                status_code=400,
                detail={
                    "message": "处理文件时出错",
                    "error": str(e)
                }
            )

    async def upload_neo4j_file_to_es(
            self,
            file: UploadFile = File(...),
            limit: int = 10,
            index_name: str = None,
            content_data_type: str = "other"
    ):
        """
        上传Neo4j文件到ES
        """
        if not index_name:
            index_name = "data_source_neo4j"

        if index_name is None:
            index_name = self.DEFAULT_INDEX_NAME

        content = await file.read()

        actions = []
        try:
            content_str = content.decode('utf-8')
            for i, line in enumerate(content_str.splitlines()):
                if i >= limit:
                    break
                if not line.strip():
                    continue
                try:
                    data = json.loads(line)
                except json.JSONDecodeError:
                    data = line

                source = {
                    "content": data
                }

                source_info_dict = {
                    "source_id": index_name,
                    "name": "Neo4j",
                    "data_type": "非结构化数据",
                    "db_type": "Neo4j",
                    "schema_table": "",
                    "table_name": "",
                }

                source["source_metadata"] = source_info_dict
                # 添加同步时间字段
                current_sync_time = datetime.now().isoformat()
                source["synced_at"] = current_sync_time
                source["data_type"] = content_data_type

                actions.append({
                    "_index": index_name,
                    "_id": str(uuid.uuid4()),
                    "_source": source
                })

            # 清空索引
            if await self.es_session.indices.exists(index=index_name):
                if not await self.delete_all_es_data(index_name=index_name):
                    return False

            # 执行批量导入
            if actions:
                success, failed = 0, 0
                try:
                    # 使用更详细的错误处理
                    async for ok, item in helpers.async_streaming_bulk(self.es_session, actions, raise_on_error=False):
                        if not ok:
                            print(f"Error indexing document: {item}")
                            failed += 1
                        else:
                            success += 1

                    # 刷新索引
                    await self.es_session.indices.refresh(index=index_name)

                    return {
                        "message": f"文件处理完成",
                        "details": {
                            "total": len(actions),
                            "success": success,
                            "failed": failed
                        }
                    }

                except Exception as e:
                    raise HTTPException(
                        status_code=500,
                        detail={
                            "message": "批量导入数据时出错",
                            "error": str(e),
                            "processed": len(actions)
                        }
                    )
            else:
                return {"message": "未找到可处理的数据"}

        except Exception as e:
            raise HTTPException(
                status_code=400,
                detail={
                    "message": "处理文件时出错",
                    "error": str(e)
                }
            )

    async def upload_binary_to_es(self, index: str, file: UploadFile = File(...)):
        """
        上传音频视频或图像文件到 Elasticsearch
        """
        if index is None:
            index = "unknown_data_binary"

        try:
            # 读取文件内容并进行 Base64 编码
            contents = await file.read()
            base64_encoded_data = base64.b64encode(contents).decode('utf-8')

            filename = file.filename
            file_extension = os.path.splitext(filename)[1].lower()

            # 简单映射一些常见的文件类型
            file_type_map = {
                '.jpg': 'image/jpeg', '.jpeg': 'image/jpeg', '.png': 'image/png',
                '.gif': 'image/gif', '.bmp': 'image/bmp',
                '.mp4': 'video/mp4', '.mov': 'video/quicktime',
                '.avi': 'video/x-msvideo', '.mkv': 'video/x-matroska',
                'mp3': 'audio/mpeg', '.wav': 'audio/wav', '.ogg': 'audio/ogg',
            }
            content_type = file_type_map.get(file_extension, file.content_type or 'application/octet-stream')

            doc = {
                "filename": filename,
                "file_type": content_type,
                "base64_data": base64_encoded_data,
                "is_binary": True
            }

            # 默认数据
            if filename == "test_image.jpg":
                doc["related_entity"] = "侯亮平"
                _id = "e85ed9ccc37655c29152ed238a6b6099"
            elif filename == "test_video.mp4":
                doc["related_entity"] = "李达康"
                _id = "5d2e88bfe7aa76fea04738d7c4e6238b"
            else:
                _id = self.generate_id(filename)

            actions = [
                {
                    "_index": index,
                    "_id": _id,
                    "_source": doc
                }
            ]

            _, failed = await async_bulk(self.es_session, actions, raise_on_error=False)
            if failed:
                raise HTTPException(
                    status_code=500,
                    detail=f"上传文件时发生错误: {failed} 条数据上传失败"
                )

            return JSONResponse(
                status_code=200,
                content={
                    "message": f"文件 '{filename}' 成功上传到 '{index}'",
                    "document_id": _id,
                }
            )

        except Exception as e:
            raise HTTPException(status_code=500, detail=f"上传文件时发生错误: {e}")

    async def download_binary_from_es(self, doc_id: str, index: str = None):
        """
        下载音频视频或图像文件
        """
        if index is None:
            raise HTTPException(status_code=404, detail="数据源id不能为空")

        try:
            response = await self.es_session.get(index=index, id=doc_id)
            if not response.get('found'):
                raise HTTPException(status_code=404, detail="文件未找到。")

            source = response['_source']
            filename = source.get('filename', 'downloaded_file')
            file_type = source.get('file_type', 'application/octet-stream')
            base64_data = source.get('base64_data')

            if not base64_data:
                raise HTTPException(status_code=500, detail="文件数据为空。")

            binary_data = base64.b64decode(base64_data)

            # 这里不需要额外修改，StreamingResponse 会根据 file_type 提供正确的 Content-Type
            return StreamingResponse(
                io.BytesIO(binary_data),
                media_type=file_type,
                headers={
                    "Content-Disposition": f"attachment; filename=\"{filename}\"",
                    "Content-Length": str(len(binary_data))
                }
            )

        except HTTPException as e:
            raise e
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"下载文件时发生错误: {e}")

    async def sync_es(self, data_source: DataSourceRequest, content_data_type: str = "text") -> bool:
        host = f"http://{data_source.ip_address}:{data_source.port}"
        remote_es_session = AsyncElasticsearch(hosts=[host])
        if not await remote_es_session.indices.exists(index=data_source.table_name):
            raise HTTPException(status_code=404, detail="索引不存在")

        if not data_source.source_id or not data_source.source_id.startswith("data_source_"):
            raise HTTPException(status_code=400, detail="数据源ID不合法")
        index_name = data_source.source_id

        query = {"query": {"match_all": {}}}
        result = helpers.async_scan(remote_es_session, index=data_source.table_name, query=query)

        source_info_dict = DataSourceModel.model_validate(data_source.model_dump()).model_dump()

        # 获取当前的同步时间，并格式化
        current_sync_time = datetime.now().isoformat()
        actions = []
        async for doc in result:
            # 获取原始文档内容
            original_source = doc.get("_source", {})

            # 深度复制原始文档以避免修改原始doc对象
            new_doc_source = original_source.copy()

            # 添加数据源信息到一个新字段，例如 'source_metadata'
            # 你可以根据需要调整这个字段名
            new_doc_source["source_metadata"] = source_info_dict
            # 添加同步时间字段
            new_doc_source["synced_at"] = current_sync_time

            # 判断是否为二进制文件
            if original_source.get("is_binary", False):
                content_data_type = "binary"

            # 添加数据类型字段
            new_doc_source["data_type"] = content_data_type

            # 准备用于批量写入的action
            # _index, _id, _source 是 bulk API 需要的字段
            actions.append({
                "_index": index_name,  # 写入到data_source.source_id
                "_id": doc.get("_id"),  # 保留原始文档ID
                "_source": new_doc_source
            })

        if not actions:
            return False

        if await self.es_session.indices.exists(index=index_name):
            # 索引存在，删除旧数据
            if not await self.delete_all_es_data(index_name=index_name):
                return False

        # 批量写入到目标ES
        # chunk_size 可以调整以优化性能，根据你的ES配置和网络情况
        _, failed = await async_bulk(self.es_session, actions, chunk_size=1000)
        if failed:
            logger.error(f"Failed to sync {len(failed)} documents from ip:{data_source.ip_address},"
                         f"index: {data_source.table_name} to"
                         f"local index: {index_name}")
            HTTPException(status_code=500, detail=f"同步失败：{len(failed)}个")

        # 立刻刷新数据
        await self.es_session.indices.refresh(index=index_name)
        return True

    async def get_data_from_es(self, page: int, page_size: int, search: str = None, index_name: str = None):
        """ 从ES中获取数据 """
        if not index_name:
            index_name = "data_source_*"

        if page < 1:
            raise ValueError("页码 (page) 必须大于等于1。")
        if page_size < 1:
            raise ValueError("每页大小 (page_size) 必须大于等于1。")

        # 计算跳过的文档数
        from_index = (page - 1) * page_size

        # 构建查询体
        query_body = {"match_all": {}}  # 默认查询所有文档

        if search:
            # 省略 'fields' 参数，让 Elasticsearch 默认搜索所有可搜索的字段
            query_body = {
                "query_string": {
                    "query": f'"{search}"',  # 强制精确匹配整个短语，不会分词
                    "fields": ["*"]  # 在所有可搜索的字段中查找
                }
            }

        try:
            # 执行ES查询
            response = await self.es_session.search(
                index=index_name,
                body={
                    "query": query_body,  # 查询所有文档，你可以根据需要添加更复杂的查询
                    "from": from_index,
                    "size": page_size,
                    "sort": [{"synced_at": {"order": "desc"}}],
                }
            )

            hits = response.get('hits', {}).get('hits', [])
            total_hits = response.get('hits', {}).get('total', {}).get('value', 0)

            data_items: List[DataManagementItem] = []
            for hit in hits:
                doc_id = hit.get('_id')
                source_data = hit.get('_source', {})

                # 尝试解析数据
                try:
                    # 提取并验证数据源信息
                    source_metadata = source_data.get('source_metadata')
                    if not source_metadata:
                        logger.warning(f"Warning: Document ID {doc_id} is missing 'source_metadata'. Skipping.")
                        continue

                    parsed_data_source = DataSourceModel(**source_metadata)

                    # 提取并验证同步时间
                    synced_at = source_data.get('synced_at')
                    if not synced_at:
                        logger.warning(f"Warning: Document ID {doc_id} is missing 'synced_at'. Skipping.")
                        continue
                    synced_at = datetime.fromisoformat(synced_at).strftime('%Y-%m-%d %H:%M:%S')

                    # 提取原始数据 (排除我们添加的元数据字段)
                    # 深拷贝原始source_data以避免修改
                    original_data = source_data.copy()

                    # 移除二进制文件数据，改为id
                    if original_data.get('is_binary', False):
                        original_data.pop('base64_data', None)
                        original_data['download_by_id'] = doc_id

                    original_data.pop('source_metadata', None)  # 移除数据源信息
                    original_data.pop('synced_at', None)  # 移除同步时间

                    # 构建 DataManagementItem 对象
                    item = DataManagementItem(
                        id=doc_id,
                        data_source=parsed_data_source,
                        data=original_data,  # 这里的 data 字段现在包含了原始 ES 文档内容
                        synced_at=synced_at
                    )
                    data_items.append(item)
                except ValidationError as e:
                    logger.error(f"Error parsing document ID {doc_id} with Pydantic: {e}")
                    # 你可以选择跳过这个文档或者记录错误
                except Exception as e:
                    logger.error(f"Unexpected error processing document ID {doc_id}: {e}")
                    # 你可以选择跳过这个文档或者记录错误

            return DataManagementListResponse(
                total=total_hits,
                data=data_items
            )

        except Exception as e:
            logger.error(f"Error during ES data retrieval: {e}")
            raise HTTPException(status_code=500, detail=f"获取数据失败{e}")

    async def update_by_es_id(self, doc_id: str, update_data: Dict[str, Any], index_name: str = None) -> bool:
        """
        根据ID更新 ES 中的单个文档
        """
        if not index_name:
            raise HTTPException(status_code=400, detail="数据源id不能为空")

        try:
            response = await self.es_session.update(
                index=index_name,
                id=doc_id,
                body={"doc": update_data}  # 使用 "doc" 来进行部分更新
            )
            if response['result'] in ['updated', 'noop']:  # 'noop' 表示文档存在但内容没有变化
                logger.info(f"文档 ID '{doc_id}' 在索引 '{index_name}' 中更新成功。结果: {response['result']}")
                # 立刻刷新数据
                await self.es_session.indices.refresh(index=index_name)
                return True
            else:
                logger.error(f"文档 ID '{doc_id}' 更新失败或结果异常: {response['result']}")
                return False
        except Exception as e:
            logger.error(f"更新文档 ID '{doc_id}' 时发生错误: {e}")
            return False

    async def delete_by_es_id(self, doc_id: str, index_name: str = None) -> bool:
        """
        根据ID删除 ES 中的单个文档
        """
        if not index_name:
            raise HTTPException(status_code=400, detail="数据源id不能为空")

        try:
            response = await self.es_session.delete(
                index=index_name,
                id=doc_id
            )
            if response['result'] == 'deleted':
                # 立刻刷新数据
                await self.es_session.indices.refresh(index=index_name)
                return True
            elif response['result'] == 'not_found':
                return False
            else:
                logger.error(f"文档 ID '{doc_id}' 删除失败或结果异常: {response['result']}")
                return False
        except Exception as e:
            print(f"删除文档 ID '{doc_id}' 时发生错误: {e}")
            return False

    async def bulk_delete_es_data_by_index(self, ids: List[str], index_name: str = None) -> bool:
        """
        从指定索引批量删除 ES 中的文档
        """
        if not index_name:
            raise HTTPException(status_code=400, detail="数据源id不能为空")

        if not ids:
            return True

        actions = []
        for doc_id in ids:
            actions.append({
                "_op_type": "delete",  # 指定操作类型为删除
                "_index": index_name,
                "_id": doc_id
            })

        try:
            _, failed = await helpers.async_bulk(self.es_session, actions)
            if failed:
                return False
            # 立刻刷新数据
            await self.es_session.indices.refresh(index=index_name)
            return True
        except Exception as e:
            logger.error(f"从索引 '{index_name}' 中批量删除文档时发生错误: {e}")
            return False

    async def bulk_delete_es_data(self, request: Dict[str, List[str]]):
        """
        批量删除 ES 中的文档
        """
        if not request:
            return True

        for index_name, ids in request.items():
            try:
                await self.bulk_delete_es_data_by_index(ids, index_name)
            except Exception as e:
                logger.error(f"批量删除文档时发生错误: {e}")
                return False
        return True

    async def delete_all_es_data(self, index_name: str = None):
        """
        删除 ES 中的所有文档
        """
        if not index_name:
            index_name = self.DEFAULT_INDEX_NAME
        try:
            await self.es_session.indices.delete(index=index_name)
            return True
        except Exception as e:
            logger.error(f"删除索引 '{index_name}' 时发生错误: {e}")
            return False

    def get_dm_schema(self, data_source: DataSourceRequest):
        """ 获取达梦数据库的schema """
        # 转义密码
        data_source.password = quote(data_source.password)
        dm_url = f"dm://{data_source.username}:{data_source.password}@{data_source.ip_address}:{data_source.port}"
        connect_args = {
            'schema': data_source.schema_table,
            'connection_timeout': 15
        }
        try:
            dm_engine = create_engine(dm_url, connect_args=connect_args, echo=True)
            dm_session = sessionmaker(bind=dm_engine, autoflush=False, autocommit=False)
            session = dm_session()
            # 获取达梦数据库的schema
            result = session.execute(text(f"SELECT * FROM {data_source.table_name} LIMIT 0"))
        except Exception as e:
            logger.error(f"获取达梦数据库的schema失败: {str(e)}")
            raise HTTPException(status_code=400, detail=f"获取达梦数据库的schema失败: {str(e)}")

        schema = result.keys()
        fields = DamengFieldsResponse(fields=[])
        for field in schema:
            fields.fields.append(field)

        try:
            session.close()
            dm_engine.dispose()
        except Exception as e:
            logger.error(f"关闭达梦数据库连接失败: {str(e)}")

        return DamengFieldsResponse(fields=fields.fields)

    async def save_dm_data_to_es(self, data_source: DataSourceRequest, content_data_type: str = "relation"):
        """ 获取达梦数据库的数据 """
        if not data_source.source_id or not data_source.source_id.startswith("data_source_"):
            raise HTTPException(status_code=400, detail="数据源id不能为空")
        index_name = data_source.source_id

        # 转义密码
        data_source.password = quote(data_source.password)
        dm_url = f"dm://{data_source.username}:{data_source.password}@{data_source.ip_address}:{data_source.port}"
        connect_args = {
            'schema': data_source.schema_table,
            'connection_timeout': 15
        }
        try:
            dm_engine = create_engine(dm_url, connect_args=connect_args, echo=True)
            dm_session = sessionmaker(bind=dm_engine, autoflush=False, autocommit=False)
            session = dm_session()

            # 获取达梦数据库的数据
            # 获取字段
            fields = ""
            if not data_source.fields:
                logger.error("达梦数据库字段为空")
                raise HTTPException(status_code=400, detail="达梦数据库字段为空")
            for field in data_source.fields:
                fields += f"{field},"
            fields = fields.rstrip(",")

            result = session.execute(text(f"SELECT {fields} FROM {data_source.table_name}"))
        except Exception as e:
            logger.error(f"获取达梦数据库的数据失败: {str(e)}")
            raise HTTPException(status_code=400, detail=f"获取达梦数据库的数据失败: {str(e)}")

        source_info_dict = DataSourceModel.model_validate(data_source.model_dump()).model_dump()

        # 获取当前的同步时间，并格式化
        current_sync_time = datetime.now().isoformat()
        actions = []
        for row in result:
            new_doc_source = {}
            for i, value in enumerate(row):
                new_doc_source[data_source.fields[i]] = value
            if not new_doc_source:
                continue

            # 添加数据源信息到一个新字段，例如 'source_metadata'
            # 你可以根据需要调整这个字段名
            new_doc_source["source_metadata"] = source_info_dict
            # 添加同步时间字段
            new_doc_source["synced_at"] = current_sync_time
            # 添加数据类型字段
            new_doc_source["data_type"] = content_data_type

            # 准备用于批量写入的action
            # _index, _id, _source 是 bulk API 需要的字段
            actions.append({
                "_index": index_name,  # 写入到data_source.source_id
                "_id": str(uuid.uuid4()),  # 保留原始文档ID
                "_source": new_doc_source
            })

        if not actions:
            return False

        if await self.es_session.indices.exists(index=index_name):
            # 删除旧数据
            if not await self.delete_all_es_data(index_name=index_name):
                return False

        # 批量写入到目标ES
        # chunk_size 可以调整以优化性能，根据你的ES配置和网络情况
        _, failed = await async_bulk(self.es_session, actions, chunk_size=1000)
        if failed:
            logger.error(f"Failed to sync {len(failed)} documents from ip:{data_source.ip_address},"
                         f"index: {data_source.table_name} to"
                         f"local index: {index_name}")
            HTTPException(status_code=500, detail=f"同步失败：{len(failed)}个")

        # 立刻刷新数据
        await self.es_session.indices.refresh(index=index_name)

        return True

    async def save_kafka_data_to_es(self, data_source: DataSourceRequest, content_data_type: str = "other"):

        if not data_source.source_id or not data_source.source_id.startswith("data_source_"):
            raise HTTPException(status_code=400, detail="数据源id不能为空")
        index_name = data_source.source_id

        # Kafka 连接和消费的默认值
        # group_id 对于 Kafka 消费者是必需的
        default_kafka_group_id: str = "default_kafka_consumer_group"
        # 默认不限制消费数量，即消费所有当前可用消息
        default_kafka_max_messages_to_consume = data_source.kafka_msg_limit if data_source.kafka_msg_limit else 500
        # 默认从最新偏移量开始消费，不从头开始
        default_kafka_start_from_beginning: bool = True

        # 从 DataSourceRequest 中提取 Kafka 相关参数
        kafka_bootstrap_servers = f"{data_source.ip_address}:{data_source.port}"
        kafka_topic = data_source.table_name  # 使用 table_name 作为 topic
        target_es_index = index_name  # 使用实例的默认索引名称

        consumer = None
        messages_consumed = 0
        es_docs_indexed = 0
        sync_successful = False  # 初始设置为失败

        logger.info(
            f"开始为主题 '{kafka_topic}' (来自 {kafka_bootstrap_servers}) 执行单次 Kafka 同步到ES索引 '{target_es_index}'...")

        source_info_dict = DataSourceModel.model_validate(data_source.model_dump()).model_dump()

        try:
            consumer = AIOKafkaConsumer(
                kafka_topic,
                bootstrap_servers=kafka_bootstrap_servers,
                group_id=default_kafka_group_id,
                auto_offset_reset='earliest' if default_kafka_start_from_beginning else 'latest',
                enable_auto_commit=True
            )
            await consumer.start()
            logger.info(f"Kafka 消费者已连接到主题 '{kafka_topic}'。")

            # 根据默认配置决定消费起始偏移量
            if default_kafka_start_from_beginning:
                await consumer.seek_to_beginning()
            else:
                await consumer.seek_to_end()

            es_actions_buffer = []
            buffer_size = 100  # 每积累100条消息就批量写入ES

            # 获取当前同步时间
            current_sync_time = datetime.now().isoformat()

            is_synced = False

            # 循环消费，直到没有更多消息或达到最大消费数量
            while True:
                messages_dict = await consumer.getmany(timeout_ms=1000, max_records=500)
                if not messages_dict:
                    logger.info("未获取到新消息，可能已消费完当前可用消息。")
                    break

                # 删除旧数据
                if not is_synced:
                    if await self.es_session.indices.exists(index=index_name):
                        if not await self.delete_all_es_data(index_name):
                            return False
                    is_synced = True

                current_batch_count = 0
                for tp, messages in messages_dict.items():
                    for message in messages:
                        try:
                            decoded_message = message.value.decode('utf-8')

                            # 修改：创建更结构化的文档
                            new_doc_source = {
                                "message": decoded_message,
                                "data_type": content_data_type,
                                "source_metadata": source_info_dict,
                                "synced_at": current_sync_time
                            }

                            doc_to_index = {
                                "_index": target_es_index,
                                "_id": str(uuid.uuid4()),
                                "_source": new_doc_source
                            }
                            es_actions_buffer.append(doc_to_index)
                            messages_consumed += 1
                            current_batch_count += 1

                            if len(es_actions_buffer) >= buffer_size:
                                logger.info(f"ES缓冲区达到 {buffer_size} 条消息，开始批量写入。")
                                _, failed = await async_bulk(self.es_session, es_actions_buffer)
                                if failed:
                                    logger.error(f"批量写入ES时失败: {len(failed)} 条消息。")
                                es_docs_indexed += (len(es_actions_buffer) - len(failed))
                                es_actions_buffer.clear()

                        except Exception as e:
                            logger.warning(f"处理Kafka消息或添加到ES缓冲区失败: {e}. 原始消息: {message.value}",
                                           exc_info=True)
                            # 继续处理下一条消息，不中断整个同步过程

                        if default_kafka_max_messages_to_consume is not None and messages_consumed >= default_kafka_max_messages_to_consume:
                            logger.info(
                                f"已达到设定的最大消费数量 {default_kafka_max_messages_to_consume} 条消息，停止消费。")
                            break

                    if default_kafka_max_messages_to_consume is not None and messages_consumed >= default_kafka_max_messages_to_consume:
                        break

                if default_kafka_max_messages_to_consume is not None and messages_consumed >= default_kafka_max_messages_to_consume:
                    break

                if current_batch_count == 0:
                    break
            # 添加：确保所有剩余的缓冲区数据都被写入ES
            if es_actions_buffer:
                logger.info(f"同步结束，刷新ES剩余缓冲区 ({len(es_actions_buffer)} 条消息)。")
                _, failed = await async_bulk(self.es_session, es_actions_buffer)
                if failed:
                    logger.error(f"同步结束时刷新ES缓冲区失败: {len(failed)} 条消息。")
                es_docs_indexed += (len(es_actions_buffer) - len(failed))

            # 添加：刷新索引以确保所有操作立即可见
            await self.es_session.indices.refresh(index=target_es_index)
            logger.info(f"已刷新索引 '{target_es_index}'，确保所有文档立即可见")

            sync_successful = True  # 如果执行到这里没有抛出异常，则认为成功
        except Exception as e:
            logger.error(f"单次 Kafka 同步操作失败: {e}", exc_info=True)
            sync_successful = False  # 出现异常，设置为失败
        finally:
            if consumer:
                await consumer.stop()
                logger.info(f"Kafka 消费者已停止。")

        logger.info(
            f"Kafka 同步完成。总共消费消息: {messages_consumed}, 索引文档: {es_docs_indexed}, 结果: {'成功' if sync_successful else '失败'}")
        return sync_successful

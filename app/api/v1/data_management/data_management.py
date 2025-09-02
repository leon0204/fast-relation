import logging
from typing import Optional

from fastapi import APIRouter, UploadFile, File, HTTPException, Depends, Query, Path, Body

from app.schemas.data_source import DbType as DataSourceDbType
from app.schemas.data_management import DataSourceRequest, DataManagementResponse, DataSourceBulkDeleteRequest
from app.controllers.data_management import DataManagementController

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/", summary="数据管理")
async def index():
    return {"message": "数据管理"}


@router.post("/sync/es", summary="同步ES数据")
async def sync_es(
        data_source: DataSourceRequest = Body(..., description="数据源信息"),
        controller: DataManagementController = Depends(),
):
    if data_source.db_type == DataSourceDbType.ES.value:
        result = await controller.sync_es(data_source)
    elif data_source.db_type == DataSourceDbType.DM.value:
        result = await controller.save_dm_data_to_es(data_source)
    elif data_source.db_type == DataSourceDbType.KAFKA.value:
        result = await controller.save_kafka_data_to_es(data_source)
    else:
        return HTTPException(status_code=400, detail="数据源类型不匹配")

    if result:
        return DataManagementResponse(msg="同步成功")
    else:
        return DataManagementResponse(msg="同步失败")


@router.get("/es/data", summary="获取ES数据")
async def get_data(
        page: int = Query(1, description="页码"),
        page_size: int = Query(10, description="每页条数"),
        search: str = Query("", description="搜索"),
        controller: DataManagementController = Depends(),
):
    return await controller.get_data_from_es(page, page_size, search)


@router.put("/es/data/{id}", summary="更新ES数据")
async def update_by_es_id(
        id: str = Path(..., description="数据ID"),
        source_id: str = Query(..., description="数据源ID"),
        data: dict = Body(..., description="更新的数据"),
        controller: DataManagementController = Depends(),
):
    result = await controller.update_by_es_id(id, data, source_id)
    if result:
        return DataManagementResponse(msg="更新成功")
    else:
        return DataManagementResponse(msg="更新失败")


@router.delete("/es/data/bulk", summary="批量删除ES数据")
async def bulk_delete_data_by_id(
        req: dict[str, list[str]] = Body(..., description="需要删除的数据ID列表"),
        controller: DataManagementController = Depends(),
):
    if not req:
        return DataManagementResponse(msg="数据ID列表为空")
    result = await controller.bulk_delete_es_data(req)
    if result:
        return DataManagementResponse(msg="删除成功")
    else:
        return DataManagementResponse(msg="删除失败")


@router.delete("/es/data/{id}", summary="删除ES数据")
async def delete_data_by_id(
        id: str = Path(..., description="数据ID"),
        source_id: str = Query(..., description="数据源ID"),
        controller: DataManagementController = Depends(),
):
    result = await controller.delete_by_es_id(id, source_id)
    if result:
        return DataManagementResponse(msg="删除成功")
    else:
        return DataManagementResponse(msg="删除失败")


@router.post("/upload/binary", summary="上传二进制数据")
async def upload_binary_to_es(
        index_name: Optional[str] = Query(None, description="Elasticsearch索引名"),
        file: UploadFile = File(...),
        controller: DataManagementController = Depends(),
):
    return await controller.upload_binary_to_es(index_name, file)


@router.get("/download/binary/{id}", summary="下载二进制数据")
async def download_binary_from_es(
        id: str = Path(..., description="数据ID"),
        source_id: str = Query(..., description="数据源ID"),
        controller: DataManagementController = Depends(),
):
    return await controller.download_binary_from_es(id, source_id)


@router.post("/dm/schema", summary="获取达梦表结构")
def get_dm_schema(
        data_source: DataSourceRequest = Body(..., description="数据源信息"),
):
    controller = DataManagementController()
    if data_source.db_type != str(DataSourceDbType.DM.value):
        return HTTPException(status_code=400, detail="数据源类型不匹配")
    return controller.get_dm_schema(data_source)


@router.post("/upload/neo4j", summary="上传Neo4j数据")
async def upload_neo4j_data(
        limit: int = Query(10, description="最多导入多少条数据"),
        file: UploadFile = File(...),
        controller: DataManagementController = Depends(),
):
    return await controller.upload_neo4j_file_to_es(file, limit)

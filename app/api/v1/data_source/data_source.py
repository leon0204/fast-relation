import logging

from fastapi import APIRouter, HTTPException, Query, Depends
from sqlalchemy.orm import Session

from app.core.dependency import AuthControl
from app.models import User
from app.schemas.data_source import (DataSourceCreateRequest, DataSourceUpdateRequest, DataSourceResponse, DataSource,
                                     DataSourceListData, DataSourceListResponse,
                                     DataSourceDeleteResponse, DataSourceBatchDeleteRequest)
from app.schemas.data_source import ConnectionTestRequest
from app.controllers.connection_test import ConnectionTester

from app.schemas.data_source import DataSourceStatus
from app.controllers.data_source import DataSourceController
from app.utils.database import get_db_session

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/", response_model=DataSourceResponse, summary="创建数据源")
def create_data_source(data: DataSourceCreateRequest, db: Session = Depends(get_db_session),
                       current_user: User = Depends(AuthControl.is_authed)):
    controller = DataSourceController(db)
    data.created_by = current_user.username
    try:
        obj = controller.create(data.model_dump())
        response = DataSourceResponse(msg="创建成功", data=DataSource(**obj))
    except Exception as e:
        # return DataSourceResponse(msg="创建失败: {}".format(str(e)), data=None)
        raise HTTPException(status_code=500, detail=str(e))
    return response


@router.get("/list", summary="查看数据源列表")
def list_data_sources(
        page: int = Query(1, ge=1, description="页码"),
        page_size: int = Query(10, ge=1, le=100, description="页数"),
        data_type: str = Query(None, description="按数据类型过滤"),
        status: int = Query(-1, description="状态：1-启用 0-禁用 -1-全部"),
        search: str = Query("", description="搜索"),
        db: Session = Depends(get_db_session),
):
    filters = {}
    if data_type:
        filters["data_type"] = data_type
    if status == DataSourceStatus.ENABLED.value:
        filters["enabled"] = DataSourceStatus.ENABLED.value
    elif status == DataSourceStatus.DISABLED.value:
        filters["enabled"] = DataSourceStatus.DISABLED.value
    else:
        pass

    controller = DataSourceController(db)
    try:
        total, data_source_list = controller.list(
            page=page,
            page_size=page_size,
            filters=filters,
            search=search.strip()
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail="查询失败")

    if not data_source_list:
        result = DataSourceListData(
            total=0,
            data=[],
        )
    else:
        data = [DataSource(**data_source) for data_source in data_source_list]
        result = DataSourceListData(
            total=total,
            data=data,
        )

    return DataSourceListResponse(
        msg="",
        data=result,
    )


@router.get("/id/{data_source_id}", response_model=DataSourceResponse, summary="查看数据源")
def get_data_source(data_source_id: int, db: Session = Depends(get_db_session)):
    controller = DataSourceController(db)
    obj = controller.get(id=data_source_id)
    if not obj:
        raise HTTPException(status_code=404, detail="数据源未找到")
    return DataSourceResponse(msg="", data=DataSource(**obj.as_dict()))


@router.put("/id/{data_source_id}", response_model=DataSourceResponse, summary="更新数据源")
def update_data_source(data_source_id: int, data: DataSourceUpdateRequest, db: Session = Depends(get_db_session)):
    controller = DataSourceController(db)
    obj = controller.get(id=data_source_id)
    if not obj:
        raise HTTPException(status_code=404, detail="数据源未找到")

    update_data = data.model_dump(exclude_unset=True)

    if update_data:
        for field, value in update_data.items():
            setattr(obj, field, value)
        controller.update(id=data_source_id, data=update_data)

    return DataSourceResponse(msg="更新成功", data=DataSource(**obj.as_dict()))


@router.delete("/id/{data_source_id}", summary="删除数据源")
def delete_data_source(data_source_id: int, db: Session = Depends(get_db_session)):
    controller = DataSourceController(db)
    deleted = controller.delete(id=data_source_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="删除失败，数据源未找到")
    return DataSourceDeleteResponse(msg="删除成功")


@router.delete("/delete/batch", response_model=DataSourceDeleteResponse, summary="批量删除数据源")
def batch_delete_data_sources(
        request: DataSourceBatchDeleteRequest,
        db: Session = Depends(get_db_session)
):
    if len(request.ids) == 0:
        return DataSourceDeleteResponse(msg="没有要删除的数据源")

    controller = DataSourceController(db)
    if controller.batch_delete(request.ids):
        return DataSourceDeleteResponse(msg="批量删除成功")
    else:
        return DataSourceDeleteResponse(msg="批量删除失败")


@router.post("/connection", summary="测试数据源连接")
async def test_connection_endpoint(request: ConnectionTestRequest):
    """测试单个服务连接"""
    result = ConnectionTester.test_connection(request)
    return result

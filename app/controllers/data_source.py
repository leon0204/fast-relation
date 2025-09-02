import uuid
from typing import List, Optional, Dict, Any, Tuple
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.models.data_source import DataSourceModel

class DataSourceController:
    def __init__(self, db: Session):
        self.db = db

    def create(self, data: Dict[str, Any]):
        """
        创建新的数据源
        """
        db_obj = DataSourceModel(
            name=data.get('name'),
            description=data.get('description'),
            data_type=data.get('data_type'),
            db_type=data.get('db_type'),
            ip_address=data.get('ip_address'),
            port=data.get('port'),
            username=data.get('username'),
            password=data.get('password'),
            schema_table=data.get('schema_table'),
            table_name=data.get('table_name'),
            enabled=data.get('enabled', True),
            created_by=data.get('created_by')
        )
        db_obj.source_id = f"data_source_{uuid.uuid4().hex[:8]}"
        returned_data = db_obj.as_dict().copy()
        try:
            self.db.add(db_obj)
            self.db.commit()
            return returned_data
        except Exception as e:
            self.db.rollback()
            raise e

    def get(self, id: int) -> Optional[DataSourceModel]:
        """
        根据ID获取单个数据源
        """
        return self.db.query(DataSourceModel).filter(DataSourceModel.id == id).first()

    def list(
        self, 
        page: int = 1, 
        page_size: int = 10, 
        filters: Optional[Dict[str, Any]] = None,
        order_by: str = '-created_at',
        search: Optional[str] = None
    ) -> Tuple[int, List[type[DataSourceModel]]]:
        """
        获取数据源列表（支持分页、过滤和搜索）
        
        :param page: 页码
        :param page_size: 每页数量
        :param filters: 精确匹配的过滤条件
        :param order_by: 排序字段，以'-'开头表示降序
        :param search: 搜索关键词，将在所有字符串字段中进行模糊匹配（密码字段除外）
        :return: (总数, 数据列表)
        """
        query = self.db.query(DataSourceModel)
        
        # 应用过滤条件
        if filters:
            for key, value in filters.items():
                if hasattr(DataSourceModel, key) and value is not None:
                    query = query.filter(getattr(DataSourceModel, key) == value)
                    
        # 应用搜索条件
        if search and search.strip():
            search = f"%{search.strip()}%"
            search_conditions = []
            
            # 定义需要搜索的字符串字段（排除密码等敏感字段）
            search_fields = [
                'name', 'description',
                'ip_address', 'schema_table', 'table_name', 'created_by'
            ]
            
            # 为每个搜索字段添加模糊匹配条件
            for field in search_fields:
                if hasattr(DataSourceModel, field):
                    search_conditions.append(getattr(DataSourceModel, field).ilike(search))
            
            # 使用OR连接所有搜索条件
            if search_conditions:
                from sqlalchemy import or_
                query = query.filter(or_(*search_conditions))
        
        # 获取总数
        total = query.count()
        
        # 应用排序
        if order_by.startswith('-'):
            order_field = order_by[1:]
            order = desc(getattr(DataSourceModel, order_field, 'created_at'))
        else:
            order = getattr(DataSourceModel, order_by, 'created_at')
        
        # 应用分页
        db_items = query.order_by(order).offset((page - 1) * page_size).limit(page_size).all()
        # 将模型对象转换为字典，确保时间字段格式正确
        items = [item.as_dict() for item in db_items]
        
        return total, items

    def update(self, id: int, data: Dict[str, Any]) -> Optional[DataSourceModel]:
        """
        更新数据源
        """
        db_obj = self.get(id)
        if not db_obj:
            return None
            
        update_data = {k: v for k, v in data.items() if v is not None}
        
        for field, value in update_data.items():
            if hasattr(db_obj, field):
                setattr(db_obj, field, value)
        
        db_obj.updated_at = datetime.now()
        
        self.db.commit()
        self.db.refresh(db_obj)
        return db_obj

    def delete(self, id: int) -> bool:
        """
        删除数据源
        """
        db_obj = self.get(id)
        if not db_obj:
            return False
            
        self.db.delete(db_obj)
        self.db.commit()
        return True

    def batch_delete(self, ids: List[int]) -> bool:
        """
        批量删除数据源

        Args:
            ids: 要删除的数据源ID列表

        Returns:
            Dict: 包含删除结果的字典
        """
        if len(ids) == 0:
            return True

        failed_ids = []

        for data_id in ids:
            try:
                # 查询数据是否存在
                db_obj = self.db.query(DataSourceModel).filter(DataSourceModel.id == data_id).first()
                if not db_obj:
                    failed_ids.append(data_id)
                    continue

                # 执行删除
                self.db.delete(db_obj)
                self.db.commit()
            except Exception as e:
                self.db.rollback()
                failed_ids.append(data_id)
                return False
        return True

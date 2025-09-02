from datetime import datetime

from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime

from app.utils.database import SQLAlchemyBase


class DataSourceModel(SQLAlchemyBase):
    __tablename__ = "data_source"
    __table_args__ = {'comment': "数据源信息表"}

    id = Column(Integer, primary_key=True, autoincrement=True, comment="数据源ID")
    source_id = Column(String(100), nullable=False, comment="数据源ID")
    name = Column(String(100), nullable=False, comment="数据源名称")
    description = Column(Text, nullable=True, comment="描述")
    data_type = Column(String(50), nullable=False, comment="数据分类：结构化/非结构化/半结构化")
    db_type = Column(String(50), nullable=False, comment="数据库类型：hbase/flink/es")
    ip_address = Column(String(100), nullable=True, comment="地址")
    port = Column(Integer, nullable=True, comment="端口号")
    username = Column(String(100), nullable=True, comment="用户名")
    password = Column(String(100), nullable=True, comment="密码")
    schema_table = Column(String(100), nullable=True, comment="库")
    table_name = Column(String(100), nullable=True, comment="表名")
    enabled = Column(Boolean, default=True, comment="当前状态")
    created_by = Column(String(100), nullable=True, comment="创建人")
    created_at = Column(DateTime, nullable=False, default=datetime.now, comment="创建时间")
    updated_at = Column(DateTime, nullable=False, default=datetime.now, onupdate=datetime.now, comment="更新时间")

    def as_dict(self):
        result = {}
        for c in self.__table__.columns:
            value = getattr(self, c.name)
            if value is not None and c.name in ['created_at', 'updated_at']:
                if hasattr(value, 'strftime'):
                    value = value.strftime("%Y-%m-%d %H:%M:%S")
            result[c.name] = value
        return result

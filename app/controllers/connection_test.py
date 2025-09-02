from urllib.parse import quote

import happybase
from elasticsearch import Elasticsearch
import requests
from kafka import KafkaAdminClient, errors
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from app.schemas.data_source import DbType, ConnectionTestRequest, TestResult


class ConnectionTester:
    @staticmethod
    def test_connection(request: ConnectionTestRequest) -> TestResult:
        """执行连接测试"""
        testers = {
            DbType.HBASE: ConnectionTester.test_hbase,
            DbType.ES: ConnectionTester.test_es,
            DbType.FLINK: ConnectionTester.test_flink,
            DbType.DM: ConnectionTester.test_dameng,
            DbType.KAFKA: ConnectionTester.test_kafka
        }

        tester = testers.get(request.db_type)
        if not tester:
            return TestResult(
                status="error",
                message=f"不支持的数据源类型: {request.db_type}"
            )

        try:
            return tester(request)
        except Exception as e:
            return TestResult(
                status="error",
                message=f"连接测试失败: {str(e)}"
            )

    @staticmethod
    def test_hbase(request: ConnectionTestRequest) -> TestResult:
        """测试HBase连接"""
        # HBase 默认端口
        port = request.port or 9090

        if not request.ip_address:
            return TestResult(
                status="error",
                message="缺少IP地址"
            )

        try:
            connection = happybase.Connection(
                host=request.ip_address,
                port=port,
                timeout=3000
            )
            tables = connection.tables()
        except Exception as e:
            return TestResult(
                status="error",
                message=f"HBase连接失败: {str(e)}"
            )
        connection.close()

        # 如果有表名参数，检查表是否存在
        if request.table_name:
            table_exists = request.table_name in tables
            message = f"HBase连接成功 | 表 '{request.table_name}' {'存在' if table_exists else '不存在'}"
        else:
            message = f"HBase连接成功 | 检测到 {len(tables)} 个表"

        return TestResult(
            status="success",
            message=message
        )

    @staticmethod
    def test_es(request: ConnectionTestRequest) -> TestResult:
        """测试Elasticsearch连接"""
        # ES 默认端口
        port = request.port or 9200

        if not request.ip_address:
            return TestResult(
                status="error",
                message="缺少IP地址"
            )

        # 处理认证
        http_auth = (request.username, request.password) if request.username and request.password else None

        # 构建连接URL
        host_url = f"http://{request.ip_address}:{port}"

        es = Elasticsearch(
            hosts=[host_url],
            http_auth=http_auth,
            verify_certs=False,
        )

        if not es.ping():
            return TestResult(
                status="error",
                message="ES Ping失败"
            )

        info = es.info()

        # 如果有索引名参数，检查索引是否存在
        if request.table_name:
            index_exists = es.indices.exists(index=request.table_name)
            message = f"ES连接成功 | 索引 '{request.table_name}' {'存在' if index_exists else '不存在'}"
        else:
            message = f"ES连接成功 | 集群: {info['cluster_name']} | 版本: {info['version']['number']}"

        return TestResult(
            status="success",
            message=message
        )

    @staticmethod
    def test_flink(request: ConnectionTestRequest) -> TestResult:
        """测试Flink连接"""
        # Flink 默认端口
        port = request.port or 8081

        if not request.ip_address:
            return TestResult(
                status="error",
                message="缺少IP地址"
            )

        # 构建基础URL
        base_url = f"http://{request.ip_address}:{port}"
        if not base_url.endswith('/'):
            base_url += '/'

        # 准备认证
        auth = (request.username, request.password) if request.username and request.password else None
        print(base_url)
        # 测试连接
        response = requests.get(f"{base_url}overview", auth=auth, timeout=5)
        print(response)

        if response.status_code == 401:
            return TestResult(
                status="error",
                message="Flink认证失败"
            )
        if response.status_code != 200:
            return TestResult(
                status="error",
                message=f"Flink返回异常状态码: {response.status_code}"
            )

        data = response.json()
        return TestResult(
            status="success",
            message=f"Flink连接成功 | 集群: {data['clusterName']} | 版本: {data['version']}"
        )

    @staticmethod
    def test_dameng(request: ConnectionTestRequest) -> TestResult:
        """测试Dameng连接"""
        if not request.ip_address or not request.port:
            return TestResult(
                status="error",
                message="缺少IP地址或端口号"
            )

        request.password = quote(request.password)
        dm_url = f"dm://{request.username}:{request.password}@{request.ip_address}:{request.port}"
        connect_args = {
            'schema': request.schema_table,
            'connection_timeout': 15
        }
        try:
            dm_engine = create_engine(dm_url, connect_args=connect_args, echo=True)
            dm_session = sessionmaker(bind=dm_engine, autoflush=False, autocommit=False)
            session = dm_session()

            result = session.execute(text(f"SELECT * FROM {request.table_name} LIMIT 0"))
            if result.keys():
                try:
                    session.close()
                    dm_engine.dispose()
                except Exception as e:
                    pass
                return TestResult(
                    status="success",
                    message=f"获取表{request.table_name}成功"
                )
            else:
                return TestResult(
                    status="error",
                    message=f"获取表{request.table_name}失败"
                )
        except Exception as e:
            return TestResult(
                status="error",
                message=f"Dameng连接失败: {str(e)}"
            )

    @staticmethod
    def test_kafka(request: ConnectionTestRequest) -> TestResult:
        """测试Kafka连接"""
        port = request.port or 9092

        if not request.ip_address:
            return TestResult(
                status="error",
                message="缺少IP地址"
            )

        bootstrap_server = f"{request.ip_address}:{port}"

        try:
            admin = KafkaAdminClient(bootstrap_servers=bootstrap_server,
                                     request_timeout_ms=3000)
            topics = admin.list_topics()
            admin.close()

            if request.table_name:
                message = f"Kafka连接成功 | 主题 '{request.table_name}' {'存在' if request.table_name in topics else '不存在'}"
            else:
                message = f"Kafka连接成功 | 发现主题数量: {len(topics)}"

            return TestResult(
                status="success",
                message=message
            )

        except errors.NoBrokersAvailable:
            return TestResult(
                status="error",
                message=f"无法连接到Kafka Broker: {bootstrap_server}"
            )
        except Exception as e:
            return TestResult(
                status="error",
                message=f"Kafka连接测试异常: {str(e)}"
            )

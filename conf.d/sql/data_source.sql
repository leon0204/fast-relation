-- 创建表结构，把SCHEMA_TABLE替换成你的schema名称
CREATE TABLE SCHEMA_TABLE."DATA_SOURCE" (
    id INT IDENTITY(1,1) PRIMARY KEY,
    source_id VARCHAR(50) NOT NULL,
    name VARCHAR(100) NOT NULL,
    description CLOB,
    data_type VARCHAR(50) NOT NULL,
    db_type VARCHAR(50) NOT NULL,
    ip_address VARCHAR(100),
    port INT,
    username VARCHAR(100),
    password VARCHAR(100),
    schema_table VARCHAR(100),
    table_name VARCHAR(100),
    enabled BIT DEFAULT 1,
    created_by VARCHAR(100),
    created_at TIMESTAMP NOT NULL,
    updated_at TIMESTAMP NOT NULL
);

-- 插入数据，把SCHEMA_TABLE替换成你的schema名称
INSERT INTO SCHEMA_TABLE.DATA_SOURCE (NAME, DESCRIPTION, DATA_TYPE, DB_TYPE, IP_ADDRESS, PORT, USERNAME, PASSWORD, SCHEMA_TABLE, TABLE_NAME, ENABLED, CREATED_BY, CREATED_AT, UPDATED_AT, SOURCE_ID) VALUES
('Elasticsearch', 'for test', '非结构化数据', 'Elasticsearch', 'elasticsearch', 9200, '', '', '', 'remote_data', 1, 'admin',
TIMESTAMP'2025-07-07 17:50:03.978469', TIMESTAMP'2025-07-22 16:38:36.115080', 'data_source_ec042fcb'),
('kafka', NULL, '非结构化数据', 'Kafka', 'kafka', 19092, '', '', '', 'test', 1, 'admin', TIMESTAMP'2025-07-18 19:29:19.956733',
TIMESTAMP'2025-07-18 19:29:19.956744', 'data_source_aac23141'),
('二进制文件同步', NULL, '非结构化数据', 'Elasticsearch', 'elasticsearch', 9200, '', '', '', 'test_for_binary', 1, 'admin',
TIMESTAMP'2025-07-21 18:58:05.696776', TIMESTAMP'2025-07-21 19:11:11.501710', 'data_source_4139df24');
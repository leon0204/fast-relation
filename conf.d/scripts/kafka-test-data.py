from kafka import KafkaProducer
import random
import json
import time

# Kafka 配置
bootstrap_servers = 'kafka:19092'
topic_name = 'test'

# 预定义的实体列表 (中文)
entities = ["张三", "李四", "王五", "赵六", "小明", "小红", "大壮", "阿花", "老王", "小李"]
# 预定义的关系列表 (中文)
relations = ["认识", "喜欢", "不喜欢", "同事", "朋友", "讨厌", "爱慕", "亲戚", "欣赏"]

# 创建 Kafka 生产者
producer = KafkaProducer(
    bootstrap_servers=[bootstrap_servers],
    value_serializer=lambda v: json.dumps(v, ensure_ascii=False).encode('utf-8')
)


def generate_random_relation():
    """生成随机关系数据"""
    entity1 = random.choice(entities)
    entity2 = random.choice(entities)
    while entity2 == entity1:  # 确保两个实体不同
        entity2 = random.choice(entities)

    relation = random.choice(relations)

    return {
        "entity1": entity1,
        "entity2": entity2,
        "relation": relation
    }


def send_data():
    """持续发送数据到 Kafka"""
    try:
        print(f"开始向 Kafka 主题 {topic_name} 发送测试数据... (Ctrl+C 停止)")
        while True:
            data = generate_random_relation()

            # 发送数据
            producer.send(topic_name, value=data)
            print(f"已发送: {data}")

            # 随机间隔 0.5-2 秒
            time.sleep(random.uniform(0.5, 2))

    except KeyboardInterrupt:
        print("\n停止发送数据")
    finally:
        producer.close()


if __name__ == '__main__':
    # 先创建主题 (如果不存在)
    from kafka.admin import KafkaAdminClient, NewTopic

    try:
        admin_client = KafkaAdminClient(bootstrap_servers=bootstrap_servers)
        topic_list = [NewTopic(name=topic_name, num_partitions=1, replication_factor=1)]
        admin_client.create_topics(new_topics=topic_list, validate_only=False)
        print(f"主题 {topic_name} 创建成功")
    except Exception as e:
        print(f"主题已存在或创建失败: {e}")

    send_data()
import os
import base64
import hashlib
from elasticsearch import Elasticsearch, helpers


def upload_test_binary_to_es(es: Elasticsearch, index: str):
    """
    从 ../binary-data 读取 test_image.jpg 和 test_video.mp4，
    编码后上传到 Elasticsearch。当前脚本应位于 conf.d/scripts 下。
    """
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "binary-data"))
    files_to_upload = [
        ("test_image.jpg", "侯亮平", "e85ed9ccc37655c29152ed238a6b6099"),
        ("test_video.mp4", "李达康", "5d2e88bfe7aa76fea04738d7c4e6238b")
    ]

    file_type_map = {
        '.jpg': 'image/jpeg', '.jpeg': 'image/jpeg', '.png': 'image/png',
        '.gif': 'image/gif', '.bmp': 'image/bmp',
        '.mp4': 'video/mp4', '.mov': 'video/quicktime',
        '.avi': 'video/x-msvideo', '.mkv': 'video/x-matroska',
        '.mp3': 'audio/mpeg', '.wav': 'audio/wav', '.ogg': 'audio/ogg',
    }

    actions = []
    for filename, related_entity, doc_id in files_to_upload:
        file_path = os.path.join(base_dir, filename)
        try:
            with open(file_path, "rb") as f:
                content = f.read()

            file_extension = os.path.splitext(filename)[1].lower()
            content_type = file_type_map.get(file_extension, 'application/octet-stream')
            base64_encoded_data = base64.b64encode(content).decode('utf-8')

            doc = {
                "filename": filename,
                "file_type": content_type,
                "base64_data": base64_encoded_data,
                "is_binary": True,
                "related_entity": related_entity
            }

            actions.append({
                "_index": index,
                "_id": doc_id,
                "_source": doc
            })

        except Exception as e:
            print(f"读取或处理文件 '{filename}' 时出错: {e}")

    if actions:
        try:
            success, errors = helpers.bulk(es, actions, raise_on_error=False)
            if errors:
                print(f"上传二进制数据时部分文档失败: {errors}")
            else:
                print(f"成功上传 {success} 个二进制文档到索引 '{index}'")
        except Exception as e:
            print(f"上传二进制数据至 Elasticsearch 时出错: {e}")
    else:
        print("没有准备好要上传的二进制文件。")


def upload_text_data_to_es(es: Elasticsearch, index: str):
    """
    清空并写入模拟文本数据到指定 Elasticsearch 索引。
    """
    if es.indices.exists(index=index):
        es.indices.delete(index=index)
        print(f"已删除旧索引: {index}")

    es.indices.create(index=index)
    print(f"已创建新索引: {index}")

    docs = [
        {
            'text': '和邓颖超在结婚前，周恩来因公务繁忙派人去车站接邓，结果没有接到，邓颖超自己找到。周恩来,生于1898年，职业是政治家。'},
        {'text': '万劫谷石屋外段延庆获救，并暗助黄眉僧，吸取部份段誉内力。段誉生于1083年，职业是大理国太子。'},
        {'text': '、侯宝林）、开场小唱（郭启儒、刘宝瑞、郭全宝、郭启儒）、空城计。侯宝林住在北京市，职业是相声演员。'},
        {'text': '张三是李四的父亲，今年50岁，职业是医生。张三住在上海，爱好是钓鱼。'},
        {'text': '《红楼梦》是曹雪芹创作的古典小说，曹雪芹生于1715年，出身于贵族家庭。曹雪芹住在南京，爱好是写诗。'},
        {'text': '刘德华和梁朝伟在电影《无间道》中合作，刘德华饰演警察，梁朝伟饰演卧底。刘德华，出生于1961年，职业是演员。'},
        {'text': '张嘉译是赵六的导师，张嘉译今年45岁，拥有博士学位。张嘉译住在杭州，爱好是读书。'},
        {'text': '李雷和韩梅梅是夫妻，李雷今年30岁，是一名工程师。李雷住在北京，爱好是打篮球。'}
    ]

    actions = [
        {
            "_index": index,
            "_id": i,
            "_source": doc
        } for i, doc in enumerate(docs)
    ]

    helpers.bulk(es, actions)
    print(f"成功上传 {len(docs)} 条文本数据到索引 '{index}'")


if __name__ == "__main__":
    remote_es = Elasticsearch("http://elasticsearch:9200")

    # 上传文本数据
    upload_text_data_to_es(remote_es, "remote_data")

    if remote_es.indices.exists(index="test_for_binary"):
        remote_es.indices.delete(index="test_for_binary")

    # 上传二进制数据
    upload_test_binary_to_es(remote_es, "test_for_binary")

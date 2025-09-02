from fastapi import APIRouter
from loguru import logger
from app.schemas.ds import  QueryItem,RelationItem
from app.schemas.base import Fail, Success

import faiss
import numpy as np

import requests

router = APIRouter()
# Ollama 的 Embedding 模型地址
EMBEDDING_MODEL_URL = "http://127.0.0.1:11434/api/embeddings"

# FAISS 索引文件路径
FAISS_INDEX_FILE = "faiss_index.bin"

# 用于存储原始文本数据（检索后构造上下文）
TEXTS_FILE = "texts.txt"


def load_or_create_faiss_index(dimension=768):
    try:
        # 尝试加载已有索引
        index = faiss.read_index(FAISS_INDEX_FILE)
        logger.info(f"FAISS 索引已加载。")
    except Exception:
        # 如果索引不存在，创建新的索引
        index = faiss.IndexFlatL2(dimension)
        logger.info(f"创建新的 FAISS 索引")

    return index


# 调用 Ollama 的 Embedding 模型生成向量
def get_embedding(text):
    payload = {
        "model": "nomic-embed-text",
        "prompt": text
    }
    response = requests.post(EMBEDDING_MODEL_URL, json=payload)
    if response.status_code == 200:
        return response.json().get("embedding", [])
    else:
        raise Exception(f"Embedding 生成失败: {response.text}")


# 构建知识库向量存储
@router.post("/upload_knowledge")
async def upload_knowledge(knowledge: list[RelationItem]):
    # 加载或创建 FAISS 索引
    """直接解析你的JSON格式数据并构建FAISS索引"""
    index = load_or_create_faiss_index()
    texts = []

    for item in knowledge:
        print(item)
        # 直接从你的JSON结构中提取数据
        h_name = item.h["name"]
        t_name = item.t["name"]
        relation = item.relation
        text_content = item.text

        # 构造用于检索的文本（保留原始信息）
        construct_text = f"关系: {relation} 人物: {h_name} 和 {t_name}  上下文: {text_content}"
        texts.append(construct_text)
        embedding = get_embedding(construct_text)
        embedding_array = np.array(embedding).reshape(1, -1)
        index.add(embedding_array)

    faiss.write_index(index, FAISS_INDEX_FILE)
    with open(TEXTS_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(texts))

    return Success(data={"items_processed": len(knowledge)})


# 从 FAISS 索引中检索相似向量
def search_faiss(query, index_file="faiss_index.bin", k=1):
    # 加载 FAISS 索引
    index = faiss.read_index(index_file)

    # 将用户问题转化为向量
    query_embedding = get_embedding(query)
    query_array = np.array(query_embedding).reshape(1, -1)

    # 在 FAISS 中检索相似向量
    distances, indices = index.search(query_array, k)

    return indices[0], distances[0]


# 调用 Ollama 的 API 生成回答
def query_ollama(prompt):
    ollama_url = "http://127.0.0.1:11434/api/generate"
    payload = {
        "model": "deepseek-r1:7b",  # 替换为你的模型名称
        "prompt": prompt,
        "stream": False
    }
    response = requests.post(ollama_url, json=payload)
    if response.status_code == 200:
        return response.json().get("response", "")
    else:
        raise Exception(f"Ollama 调用失败: {response.text}")


# 根据检索结果构造 Prompt 并生成回答
def generate_answer(query, texts, indices):
    # 检索到的文本
    retrieved_texts = [texts[i] for i in indices]
    logger.info(f"上下文: {retrieved_texts}")


    #TODO 这里只获取到第二行了，上下文

    # 构造 Prompt：将检索到的信息作为上下文
    context = "\n".join(
        [f"问题: {item.split(' ', 1)[0] if ' ' in item else item}\n答案: {item.split(' ', 1)[1] if ' ' in item else ''}" for
         item in retrieved_texts])
    prompt = f"根据以下上下文回答问题：\n\n{context}\n\n用户问题：{query}\n\n模型回答："

    # 调用 Ollama
    return query_ollama(prompt)


# 查询接口
@router.post("/query")
async def query(query_item: QueryItem):
    # 接收用户提交的问题
    query_text = query_item.question
    logger.info(f"用户提问: {query_text}")

    index = load_or_create_faiss_index()
    logger.info(f"加载 FAISS 索引: {index}")

    with open(TEXTS_FILE, 'r', encoding='utf-8') as f:
        texts = f.read().splitlines()  # 从文件中加载原始文本数据

    # 检索知识库
    indices, distances = search_faiss(query_text)
    logger.info(indices)
    logger.info(distances)


    # 生成回答
    logger.info(f"生成回答")
    answer = generate_answer(query_text, texts, indices)

    return {"answer": answer}

import hashlib
import base64
import json
import datetime
import warnings

from typing import Optional
from contextlib import asynccontextmanager

from elasticsearch import Elasticsearch, helpers, ElasticsearchWarning
from fastapi import FastAPI, Request, UploadFile, File, HTTPException, Query


# 忽略安全相关警告（可选）
warnings.filterwarnings("ignore", category=ElasticsearchWarning)

es_host = "http://localhost:9200"

INDEX_NAME = "unknown_data"
REMOTE_INDEX_NAME = "remote_data"

def generate_id(content_str: str) -> str:
    return hashlib.md5(content_str.encode("utf-8")).hexdigest()

def prepare_doc(data):
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

    doc_id = generate_id(content_str)
    return {
        "_index": INDEX_NAME,
        "_id": doc_id,
        "_source": {
            "content": content_str,
            "raw": raw_data,
            "timestamp": datetime.datetime.utcnow().isoformat()
        }
    }

# es session 生命周期
@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.es_session = Elasticsearch(es_host)
    if not app.state.es_session.indices.exists(index=INDEX_NAME):
        app.state.es_session.indices.create(index=INDEX_NAME)
    yield

    app.state.es_session.close()

app = FastAPI(lifespan=lifespan)

@app.get("/")
async def index():
    return {"message": "For Elasticsearch Use"}

@app.post("/sync/es")
async def sync_es(
    request: Request,
    remote_es_host: str = Query("", description="远程ES地址，如 http://localhost:9200"),
    remote_index: str = Query("", description="远程索引名"),
    limit: int = Query(-1, description="最多导入多少条数据")
):
    try:
        # 切到本地
        if remote_index.strip() == "":
            remote_index = REMOTE_INDEX_NAME
        if remote_es_host.strip() == "":
            remote_es_host = es_host

        remote_es = Elasticsearch(remote_es_host)
        if not remote_es.indices.exists(index=remote_index):
            raise HTTPException(status_code=404, detail="远程索引不存在")

        query = {"query": {"match_all": {}}}
        result = helpers.scan(remote_es, index=remote_index, query=query)

        actions = []
        count = 0
        for doc in result:
            doc_data = doc.get("_source", {})
            actions.append(prepare_doc(doc_data))
            count += 1
            if 0 < limit <= count:
                break

        es_session: Elasticsearch = request.app.state.es_session
        helpers.bulk(es_session, actions)

        # 立刻刷新数据
        es_session.indices.refresh(index=INDEX_NAME)

        return {"message": f"成功从远程索引导入 {count} 条数据"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"导入失败: {str(e)}")

@app.post("/upload/file")
async def upload_file(request: Request, file: UploadFile = File(...)):
    es_session: Elasticsearch = request.app.state.es_session
    content = await file.read()

    actions = []
    try:
        # 尝试解析为JSON
        try:
            data = json.loads(content)
            if isinstance(data, list):
                actions = [prepare_doc(item) for item in data]
            else:
                actions = [prepare_doc(data)]
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
                actions.append(prepare_doc(data))

        # 批量导入前先检查索引是否存在
        if not es_session.indices.exists(index=INDEX_NAME):
            es_session.indices.create(index=INDEX_NAME)

        # 执行批量导入
        if actions:
            success, failed = 0, 0
            try:
                # 使用更详细的错误处理
                for ok, item in helpers.streaming_bulk(es_session, actions, raise_on_error=False):
                    if not ok:
                        print(f"Error indexing document: {item}")
                        failed += 1
                    else:
                        success += 1

                # 刷新索引
                es_session.indices.refresh(index=INDEX_NAME)

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

@app.post("/upload/json")
async def upload_json_data(request: Request):
    es: Elasticsearch = request.app.state.es_session
    try:
        data = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="请求体必须是合法JSON")

    if not isinstance(data, list):
        data = [data]

    actions = [prepare_doc(d) for d in data]
    helpers.bulk(es, actions)

    return {"message": f"成功存储 {len(actions)} 条数据"}

@app.get("/search")
def search(request: Request, q: Optional[str] = Query(None, description="搜索关键词")):
    es: Elasticsearch = request.app.state.es_session

    if not q:
        raise HTTPException(status_code=400, detail="缺少查询参数 q")

    query = {
        "query": {
            "match": {
                "content": q
            }
        }
    }

    resp = es.search(index=INDEX_NAME, body=query)
    hits = resp.get("hits", {}).get("hits", [])
    return {"total": len(hits), "results": [hit["_source"] for hit in hits]}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=9888)

from fastapi import FastAPI, HTTPException, Response
from pydantic import BaseModel, HttpUrl
import httpx
from urllib.parse import urlparse
import os
import logging

app = FastAPI()

# 设置日志记录
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# 请求模型类
class ProxyRequest(BaseModel):
    code: str
    url: HttpUrl


# 响应模型类
class ProxyResponse(BaseModel):
    status_code: int
    content: str
    headers: dict


# 校验密钥
SECRET_CODE = os.getenv("SECRET_CODE")

if not SECRET_CODE:
    logger.error("SECRET_CODE environment variable is not set. Exiting.")
    raise SystemExit("SECRET_CODE environment variable is required.")

# 打印密钥到日志中
logger.info(f"SECRET_CODE: {SECRET_CODE}")


def verify_code(code: str):
    if code != SECRET_CODE:
        raise HTTPException(status_code=403, detail="Invalid code")


# 反向代理请求处理函数
async def proxy_request(url: str) -> ProxyResponse:
    async with httpx.AsyncClient() as client:
        response = await client.get(str(url))
        return ProxyResponse(
            status_code=response.status_code,
            content=response.text,
            headers=dict(response.headers),
        )


@app.get('/')
async def status():
    return {'status': 'ok'}

# 端点 "/img"
@app.get("/img")
async def proxy_img(code: str, url: HttpUrl):
    verify_code(code)
    if urlparse(str(url)).netloc != "hi77-overseas.mangafuna.xyz":
        raise HTTPException(status_code=400, detail="Invalid URL")
    async with httpx.AsyncClient() as client:
        response = await client.get(str(url))
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail="Failed to fetch image")
        return Response(content=response.content, media_type=response.headers.get('content-type'))


# 端点 "/api"
@app.get("/api")
async def proxy_api(code: str, url: HttpUrl):
    verify_code(code)
    if urlparse(str(url)).netloc != "api.mangacopy.com":
        raise HTTPException(status_code=400, detail="Invalid URL")
    async with httpx.AsyncClient() as client:
        response = await client.get(str(url))
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail="Failed to fetch data")
        return Response(content=response.content, media_type=response.headers.get('content-type'))
# 运行命令：uvicorn filename:app --reload
# 请将 "your_secret_code" 替换为您的实际密钥，并将 "filename" 替换为您的 Python 文件名。

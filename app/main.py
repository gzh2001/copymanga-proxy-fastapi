from fastapi import FastAPI, HTTPException, Response
from pydantic import BaseModel, HttpUrl
import httpx
from urllib.parse import urlparse
import re
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
        logger.warning(f"Invalid code provided: {code}")
        raise HTTPException(status_code=403, detail="Invalid code")


# 匹配的URL模式
API_URL_PATTERN = r"^https://api\.(copymanga|mangacopy)\.\w+/api/"
IMG_URL_PATTERN = r"^https://hi77-overseas\.mangafuna\.xyz"


# 反向代理请求处理函数
async def proxy_request(url: str) -> ProxyResponse:
    logger.debug(f"Proxying request to URL: {url}")
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(str(url))
            response.raise_for_status()
        except httpx.HTTPStatusError as exc:
            logger.error(f"HTTP error occurred while fetching URL {url}: {exc}")
            raise HTTPException(status_code=exc.response.status_code, detail=f"Error fetching URL: {exc}")
        except httpx.RequestError as exc:
            logger.error(f"Request error occurred while fetching URL {url}: {exc}")
            raise HTTPException(status_code=500, detail=f"An error occurred while requesting {url}: {exc}")
        logger.debug(f"Successfully fetched URL: {url} with status code {response.status_code}")
        return ProxyResponse(
            status_code=response.status_code,
            content=response.text,
            headers=dict(response.headers),
        )


@app.get('/')
async def status():
    logger.debug("Status endpoint called")
    return {'status': 'ok'}


# 端点 "/img"
@app.get("/img")
async def proxy_img(code: str, url: HttpUrl):
    logger.debug(f"/img endpoint called with URL: {url}")
    verify_code(code)
    if not re.match(IMG_URL_PATTERN, str(url)):
        logger.warning(f"Invalid URL provided for /img endpoint: {url}")
        raise HTTPException(status_code=400, detail="Invalid URL")
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(str(url))
            response.raise_for_status()
        except httpx.HTTPStatusError as exc:
            logger.error(f"HTTP error occurred while fetching image URL {url}: {exc}")
            raise HTTPException(status_code=exc.response.status_code, detail=f"Failed to fetch image: {exc}")
        except httpx.RequestError as exc:
            logger.error(f"Request error occurred while fetching image URL {url}: {exc}")
            raise HTTPException(status_code=500, detail=f"An error occurred while requesting {url}: {exc}")
        logger.debug(f"Successfully fetched image from URL: {url} with status code {response.status_code}")
        return Response(content=response.content, media_type=response.headers.get('content-type'))


# 端点 "/api"
@app.get("/api")
async def proxy_api(code: str, url: HttpUrl):
    logger.debug(f"/api endpoint called with URL: {url}")
    verify_code(code)
    # 【修改的部分】
    if not re.match(API_URL_PATTERN, str(url)):
        logger.warning(f"Invalid URL provided for /api endpoint: {url}")
        raise HTTPException(status_code=400, detail="Invalid URL")
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(str(url))
            response.raise_for_status()
        except httpx.HTTPStatusError as exc:
            logger.error(f"HTTP error occurred while fetching API URL {url}: {exc}")
            raise HTTPException(status_code=exc.response.status_code, detail=f"Failed to fetch data: {exc}")
        except httpx.RequestError as exc:
            logger.error(f"Request error occurred while fetching API URL {url}: {exc}")
            raise HTTPException(status_code=500, detail=f"An error occurred while requesting {url}: {exc}")
        logger.debug(f"Successfully fetched data from URL: {url} with status code {response.status_code}")
        return Response(content=response.content, media_type=response.headers.get('content-type'))
# 运行命令：uvicorn filename:app --reload
# 请将 "your_secret_code" 替换为您的实际密钥，并将 "filename" 替换为您的 Python 文件名。

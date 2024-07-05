import logging
import random
import re
import httpx
from fastapi import FastAPI, Request, Response
import string
import os

# from pydantic import BaseModel
from pydantic import BaseModel, field_validator, AnyUrl, ValidationError
from starlette.responses import JSONResponse

app = FastAPI()
alphabet = string.ascii_letters + string.digits
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 获取环境变量
IMG_PATTERN = os.getenv("HOST_PATTERN", r".*\.mangafuna\.xyz")
API_PATTERN = os.getenv("HOST_PATTERN", r"^https://api\.(copymanga|mangacopy)\.\w+/api/")
APIKEY = os.getenv("APIKEY", ''.join(random.sample(alphabet, 32)))
logger.info("APIKEY: %s", APIKEY)


class imgItem(BaseModel):
    code: str
    url: AnyUrl

    @field_validator('code')
    def check_code(cls, code):
        if code != APIKEY:
            raise ValueError('code error')
        return code

    @field_validator('url')
    def is_valid_host(cls, url):
        pattern = re.compile(IMG_PATTERN)
        if pattern.match(url) is None:
            raise ValueError('网站地址错误')
        return url


class apiItem(BaseModel):
    code: str
    url: AnyUrl

    @field_validator('code')
    def check_code(cls, code):
        if code != APIKEY:
            raise ValueError('code error')
        return code

    @field_validator('url')
    def is_valid_host(cls, url):
        pattern = re.compile(API_PATTERN)
        if pattern.match(url) is None:
            raise ValueError('网站地址错误')
        return url


# 自定义异常处理器
@app.exception_handler(ValidationError)
async def validation_exception_handler(request, exc):
    details = exc.errors()
    logger.debug(details)
    for detail in details:
        if detail['type'] == 'value_error':
            return JSONResponse(
                status_code=422,
                content={"message": "Validation Error: Invalid value"},
            )
        # 可以添加更多条件来处理不同类型的验证错误
    return JSONResponse(
        status_code=400,
        content={"message": "Bad Request: Validation error"},
    )


def checkToken(code: str):
    if code == APIKEY:
        return True
    else:
        return False


def checkURL(url: str, pattern: str):
    pattern = re.compile(pattern)
    if pattern.match(url) is None:
        return False
    else:
        return True


@app.get("/", status_code=200)
async def root():
    return {"message": "Server is up"}


@app.get("/proxy/img/", status_code=200)
async def img(code: str, url: AnyUrl):
    if not checkToken(code):
        return JSONResponse(
            status_code=401,
            content={"message": "Error Token"},
        )

    if not checkURL(str(url), IMG_PATTERN):
        return JSONResponse(
            status_code=404,
            content={"message": "Invalid URL"},
        )

    # 创建 httpx 异步客户端
    async with httpx.AsyncClient() as client:
        # 转发请求到目标服务器
        proxy_response = await client.request(
            method='GET',
            url=str(url)
        )

        # 返回目标服务器的响应
        return Response(
            content=proxy_response.content,
            status_code=proxy_response.status_code,
            headers=proxy_response.headers
        )


@app.get("/proxy/api/", status_code=200)
async def api(code: str, url: AnyUrl):
    if not checkToken(code):
        return JSONResponse(
            status_code=401,
            content={"message": "Error Token"},
        )

    if not checkURL(str(url), API_PATTERN):
        return JSONResponse(
            status_code=404,
            content={"message": "Invalid URL"},
        )
    # 创建 httpx 异步客户端
    async with httpx.AsyncClient() as client:
        # 转发请求到目标服务器
        proxy_response = await client.request(
            method='GET',
            url=str(url)
        )

        # 返回目标服务器的响应
        return Response(
            content=proxy_response.content,
            status_code=proxy_response.status_code,
            headers=proxy_response.headers
        )

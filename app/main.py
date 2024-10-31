from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, HttpUrl
import httpx

app = FastAPI()

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
SECRET_CODE = "111111"

def verify_code(code: str):
    if code != SECRET_CODE:
        raise HTTPException(status_code=403, detail="Invalid code")

# 反向代理请求处理函数
async def proxy_request(url: HttpUrl) -> ProxyResponse:
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        return ProxyResponse(
            status_code=response.status_code,
            content=response.text,
            headers=dict(response.headers),
        )

# 端点 "/img"
@app.get("/img", response_model=ProxyResponse)
async def proxy_img(code: str, url: HttpUrl):
    verify_code(code)
    if not url.startswith("https://hi77-overseas.mangafuna.xyz/"):
        raise HTTPException(status_code=400, detail="Invalid URL")
    return await proxy_request(url)

# 端点 "/api"
@app.post("/api", response_model=ProxyResponse)
async def proxy_api(request: ProxyRequest):
    verify_code(request.code)
    if not request.url.startswith("https://api.mangacopy.com/"):
        raise HTTPException(status_code=400, detail="Invalid URL")
    return await proxy_request(request.url)

# 运行命令：uvicorn filename:app --reload
# 请将 "your_secret_code" 替换为您的实际密钥，并将 "filename" 替换为您的 Python 文件名。

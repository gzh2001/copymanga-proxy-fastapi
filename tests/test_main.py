from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)
token = "Aa147258"

def test_read_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {'status': 'ok'}

def test_image_api():
    response = client.get(f"/img?code={token}&url=https://hi77-overseas.mangafuna.xyz/tajueduishixihuanzhewode/6149d/1648197052030006.jpg.c800x.webp")
    assert response.status_code == 200
    assert response.headers['Content-Type'] == 'image/webp'

# def test_webapi_api():
#     response = client.get("/webapi")
# tests/test_plugs.py
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.services.pyp100 import pyp100_service

client = TestClient(app)

@pytest.fixture(autouse=True)
def stub_pyp100(monkeypatch):
    # 네트워크 호출 대신 간단한 반환값을 사용하도록 메서드 모킹
    monkeypatch.setattr(pyp100_service, "turn_on", lambda name: True)
    monkeypatch.setattr(pyp100_service, "turn_off", lambda name: False)
    monkeypatch.setattr(pyp100_service, "get_status", lambda name: True)

@pytest.fixture(scope="module")
def token():
    response = client.post(
        "/auth/login",
        data={"username": "uhyun", "password": "secret"},
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    assert response.status_code == 200
    return response.json()["access_token"]

def test_list_plugs(token):
    headers = {"Authorization": f"Bearer {token}"}
    response = client.get("/plugs/", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert data and "name" in data[0] and "ip" in data[0]

def test_power_on(token):
    headers = {"Authorization": f"Bearer {token}"}
    response = client.post("/plugs/uhyun/on", headers=headers)
    assert response.status_code == 200
    assert response.json()["status"] is True

def test_power_off(token):
    headers = {"Authorization": f"Bearer {token}"}
    response = client.post("/plugs/uhyun/off", headers=headers)
    assert response.status_code == 200
    assert response.json()["status"] is False

def test_power_status(token):
    headers = {"Authorization": f"Bearer {token}"}
    response = client.get("/plugs/uhyun/status", headers=headers)
    assert response.status_code == 200
    assert response.json()["status"] is True

@ pytest.mark.parametrize("endpoint, method", [
    ("/plugs/unknown/on", "post"),
    ("/plugs/unknown/off", "post"),
    ("/plugs/unknown/status", "get")
])
def test_invalid_plug(token, endpoint, method):
    headers = {"Authorization": f"Bearer {token}"}
    response = client.request(method, endpoint, headers=headers)
    assert response.status_code == 404

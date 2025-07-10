import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_login_success():
    """로그인 성공 테스트"""
    response = client.post(
        "/auth/login",
        data={"username": "admin", "password": "admin123"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

def test_login_invalid_credentials():
    """잘못된 인증정보로 로그인 실패 테스트"""
    response = client.post(
        "/auth/login",
        data={"username": "wrong", "password": "wrong"}
    )
    assert response.status_code == 401
    assert "Incorrect username or password" in response.json()["detail"]

def test_protected_endpoint_without_token():
    """토큰 없이 보호된 엔드포인트 접근 테스트"""
    response = client.get("/plugs/")
    assert response.status_code == 401

def test_protected_endpoint_with_token():
    """토큰으로 보호된 엔드포인트 접근 테스트"""
    # 먼저 로그인하여 토큰 획득
    login_response = client.post(
        "/auth/login",
        data={"username": "admin", "password": "admin123"}
    )
    token = login_response.json()["access_token"]
    
    # 토큰으로 보호된 엔드포인트 접근
    response = client.get(
        "/plugs/",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200 
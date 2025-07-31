"""
基础测试文件
"""
import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_health_check():
    """测试健康检查接口"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"


def test_root_endpoint():
    """测试根路径"""
    response = client.get("/")
    assert response.status_code == 200


def test_docs_endpoint():
    """测试API文档"""
    response = client.get("/docs")
    assert response.status_code == 200


def test_ip_query_basic():
    """测试基础IP查询"""
    # 测试本地IP
    response = client.get("/api/ip/127.0.0.1")
    assert response.status_code == 200
    
    # 测试无效IP
    response = client.get("/api/ip/invalid-ip")
    assert response.status_code == 422


def test_batch_ip_query():
    """测试批量IP查询"""
    test_data = {
        "ips": ["127.0.0.1", "8.8.8.8"]
    }
    response = client.post("/api/ip/batch", json=test_data)
    assert response.status_code == 200
    data = response.json()
    assert len(data["results"]) == 2


def test_admin_auth_endpoint():
    """测试管理员认证接口"""
    # 测试无效凭据
    response = client.post("/api/admin/auth/login", json={
        "username": "invalid",
        "password": "invalid"
    })
    assert response.status_code == 401
    
    # 测试有效凭据
    response = client.post("/api/admin/auth/login", json={
        "username": "admin",
        "password": "admin123"
    })
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data

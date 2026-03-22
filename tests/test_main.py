"""Tests for main application"""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_health_check():
    """Test health check endpoint"""
    from app.main import app
    
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "version" in data
        assert "environment" in data


@pytest.mark.asyncio
async def test_root_endpoint():
    """Test root endpoint"""
    from app.main import app
    
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "version" in data
        assert "docs" in data


@pytest.mark.asyncio
async def test_api_status():
    """Test API status endpoint"""
    from app.main import app
    
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/api/v1/status")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "operational"
        assert data["version"] == "1.0.0"

import pytest
from httpx import AsyncClient
from main import app

@pytest.mark.asyncio
async def test_root():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Welcome to The New Hire API"}

@pytest.mark.asyncio
async def test_github_login_url():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/api/auth/github/login")
    assert response.status_code == 200
    assert "https://github.com/login/oauth/authorize" in response.json()["url"]

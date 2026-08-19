"""
Tutunaku - Suite de pruebas integradas
"""
import pytest
from sqlalchemy import text
from app.core.database import get_mysql_engine, get_mongo_db

@pytest.mark.asyncio
async def test_api_and_database_integrity(client):
    """Prueba integral de la API, conectividad y base de datos."""
    
    # 1. Checar Salud de la API
    health_resp = await client.get("/health")
    assert health_resp.status_code == 200
    assert health_resp.json()["status"] == "ok"
    
    # 2. Checar MySQL
    engine = get_mysql_engine()
    async with engine.connect() as conn:
        res = await conn.execute(text("SELECT 1"))
        assert res.scalar() == 1
    
    # 3. Checar MongoDB
    mongodb = get_mongo_db()
    ping = await mongodb.command("ping")
    assert ping["ok"] == 1.0
    
    # 4. Checar Login
    login_data = {"email": "admin@tutunaku.mx", "password": "Admin1234!"}
    login_resp = await client.post("/api/v1/auth/login", json=login_data)
    assert login_resp.status_code == 200
    assert "access_token" in login_resp.json()

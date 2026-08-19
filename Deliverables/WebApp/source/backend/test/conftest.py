"""
Tutunaku - Configuración de Pytest y Fixtures
Incluye el cliente de prueba y dependencias para los tests.
"""
import pytest
from typing import AsyncGenerator
from httpx import AsyncClient, ASGITransport
from app.main import create_application
from app.core.config import settings

@pytest.fixture(scope="session")
async def app():
    """Fixture que retorna la aplicación FastAPI configurada."""
    from app.core.database import close_db
    _app = create_application()
    yield _app
    # Teardown: cerrar conexiones a bases de datos
    await close_db()

@pytest.fixture(scope="session")
async def client(app) -> AsyncGenerator[AsyncClient, None]:
    """Fixture que proporciona un cliente HTTP asíncrono para pruebas."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

@pytest.fixture(scope="session")
def test_settings():
    """Proporciona la configuración actual para validación."""
    return settings

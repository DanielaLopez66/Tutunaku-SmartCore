"""
Tutunaku - Configuración central de la aplicación
Usa Pydantic Settings para validar variables de entorno
"""
import os
from pathlib import Path
from typing import Literal

from pydantic import EmailStr
from pydantic_settings import BaseSettings

# Raíz del repositorio (…/tutunakun/tutunakun), usada para ubicar por defecto
# los artefactos de Machine Learning (models/serialized) y el Data Warehouse
# analítico (database/warehouse), que viven fuera de Deliverables/WebApp. Solo
# existen 6 ancestros en el layout del monorepo local; en un contenedor
# (Dockerfile copia backend/ directo a /app) esa profundidad no existe, así
# que ML_MODEL_DIR/ML_WAREHOUSE_DB se pasan explícitos por entorno ahí (ver
# deploy/docker-compose.yml) y este valor por defecto nunca llega a usarse.
try:
    _REPO_ROOT = Path(__file__).resolve().parents[6]
except IndexError:
    _REPO_ROOT = Path(__file__).resolve().parent


class Settings(BaseSettings):
    """Configuración principal de la aplicación."""

    # App
    APP_NAME: str = "Tutunaku API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    SECRET_KEY: str = "dev_secret_key_change_in_production_32chars"
    ENVIRONMENT: Literal["development", "staging", "production"] = "development"

    # Base de datos
    DB_TYPE: Literal["mysql", "mongodb", "both"] = "both"

    # MySQL
    MYSQL_HOST: str = "localhost"
    MYSQL_PORT: int = 3306
    MYSQL_USER: str = "root"
    MYSQL_PASSWORD: str = ""
    MYSQL_DATABASE: str = "tutunakun_db"

    # MongoDB
    MONGODB_URL: str = "mongodb://localhost:27017"
    MONGODB_DATABASE: str = "tutunakun_db"

    # JWT
    JWT_SECRET_KEY: str = "jwt_secret_key_change_in_production_32chars"
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # Email
    MAIL_USERNAME: str = ""
    MAIL_PASSWORD: str = ""
    MAIL_FROM: str = "noreply@tutunaku.mx"
    MAIL_PORT: int = 587
    MAIL_SERVER: str = "smtp.gmail.com"
    MAIL_TLS: bool = True
    MAIL_SSL: bool = False

    # Frontend
    FRONTEND_URL: str = "http://localhost:5173"

    # Hosts confiables para TrustedHostMiddleware (solo aplica si DEBUG=false),
    # separados por coma. Incluye localhost/127.0.0.1 a propósito: el
    # HEALTHCHECK del propio contenedor Docker llega con ese Host, no con el
    # dominio público (ver backend/Dockerfile y deploy/docker-compose.yml).
    ALLOWED_HOSTS_RAW: str = "tutunaku.mx,*.tutunaku.mx,localhost,127.0.0.1"

    # Rate limiting
    RATE_LIMIT_PER_MINUTE: int = 60

    # APScheduler corre en memoria por proceso: con varias réplicas detrás
    # del balanceador (ver Deliverables/WebApp/DeployManual), cada una
    # dispararía los mismos jobs por duplicado. Solo la réplica designada
    # como "líder" en docker-compose la deja en true.
    ENABLE_SCHEDULER: bool = True

    # Archivos
    UPLOAD_DIR: str = "uploads"
    MAX_FILE_SIZE_MB: int = 10

    # Machine Learning - API inteligente (/api/ml)
    ML_MODEL_DIR: str = str(_REPO_ROOT / "models" / "serialized")
    ML_WAREHOUSE_DB: str = str(_REPO_ROOT / "database" / "warehouse" / "tutunaku_dw.sqlite")

    # Dashboard en tiempo real (Socket.IO): intervalos cortos a propósito para
    # que los eventos automáticos sean visibles rápido en desarrollo/demo.
    # Súbelos (ej. 300 / 120) en un despliegue real de mayor escala.
    ML_PLATFORM_LOAD_INTERVAL_SECONDS: int = 20
    ML_USER_PROGRESS_INTERVAL_SECONDS: int = 15

    @property
    def MYSQL_DATABASE_URL(self) -> str:
        """Retorna la URL de conexión para SQLAlchemy (MySQL)."""
        return (
            f"mysql+pymysql://{self.MYSQL_USER}:{self.MYSQL_PASSWORD}"
            f"@{self.MYSQL_HOST}:{self.MYSQL_PORT}/{self.MYSQL_DATABASE}"
            f"?charset=utf8mb4"
        )

    @property
    def ALLOWED_HOSTS(self) -> list[str]:
        """Lista de hosts confiables a partir de ALLOWED_HOSTS_RAW."""
        return [h.strip() for h in self.ALLOWED_HOSTS_RAW.split(",") if h.strip()]

    @property
    def MAX_FILE_SIZE_BYTES(self) -> int:
        """Retorna el tamaño máximo de archivo en bytes."""
        return self.MAX_FILE_SIZE_MB * 1024 * 1024

    class Config:
        """Configuración de Pydantic Settings."""
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


# Instancia global de configuración
settings = Settings()

# Crear directorio de uploads si no existe
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)

"""
Tutunaku - Manejo global de excepciones
Respuestas de error consistentes en toda la API
"""
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import SQLAlchemyError
import structlog

logger = structlog.get_logger()


class TutunakuException(Exception):
    """Excepción base del sistema Tutunaku."""
    def __init__(self, message: str, status_code: int = 400, code: str = "ERROR"):
        self.message = message
        self.status_code = status_code
        self.code = code
        super().__init__(message)


class NotFoundError(TutunakuException):
    def __init__(self, resource: str = "Recurso"):
        super().__init__(f"{resource} no encontrado", 404, "NOT_FOUND")


class UnauthorizedError(TutunakuException):
    def __init__(self, message: str = "No autorizado"):
        super().__init__(message, 401, "UNAUTHORIZED")


class ForbiddenError(TutunakuException):
    def __init__(self, message: str = "Acceso denegado"):
        super().__init__(message, 403, "FORBIDDEN")


class ConflictError(TutunakuException):
    def __init__(self, message: str = "Conflicto de datos"):
        super().__init__(message, 409, "CONFLICT")


class ValidationError(TutunakuException):
    def __init__(self, message: str = "Datos inválidos"):
        super().__init__(message, 422, "VALIDATION_ERROR")


class MLModelUnavailableError(TutunakuException):
    """El modelo solicitado no está cargado (archivo faltante o corrupto)."""
    def __init__(self, model_name: str = "modelo"):
        super().__init__(
            f"El modelo '{model_name}' no está disponible en este momento",
            503,
            "ML_MODEL_UNAVAILABLE",
        )


class MLInferenceError(TutunakuException):
    """La inferencia no pudo completarse (entrada inválida para el modelo)."""
    def __init__(self, message: str = "No se pudo completar la inferencia"):
        super().__init__(message, 422, "ML_INFERENCE_ERROR")


def register_exception_handlers(app: FastAPI):
    """Registra todos los manejadores de excepciones."""

    @app.exception_handler(TutunakuException)
    async def tutunaku_exception_handler(request: Request, exc: TutunakuException):
        logger.warning(
            "tutunaku_exception",
            code=exc.code,
            message=exc.message,
            path=str(request.url),
        )
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "success": False,
                "error": {
                    "code": exc.code,
                    "message": exc.message,
                },
            },
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        errors = []
        for error in exc.errors():
            field = " → ".join(str(loc) for loc in error["loc"])
            errors.append({"field": field, "message": error["msg"]})

        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "success": False,
                "error": {
                    "code": "VALIDATION_ERROR",
                    "message": "Error de validación en los datos enviados",
                    "details": errors,
                },
            },
        )

    @app.exception_handler(SQLAlchemyError)
    async def sqlalchemy_exception_handler(request: Request, exc: SQLAlchemyError):
        logger.error("database_error", error=str(exc), path=str(request.url))
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "success": False,
                "error": {
                    "code": "DATABASE_ERROR",
                    "message": "Error interno de base de datos",
                },
            },
        )

    @app.exception_handler(Exception)
    async def generic_exception_handler(request: Request, exc: Exception):
        logger.error("unexpected_error", error=str(exc), path=str(request.url))
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "success": False,
                "error": {
                    "code": "INTERNAL_ERROR",
                    "message": "Error interno del servidor",
                },
            },
        )

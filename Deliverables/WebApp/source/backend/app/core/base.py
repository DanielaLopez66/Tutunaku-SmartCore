"""
Tutunaku - SQLAlchemy Base class
Declarado en un archivo separado para evitar importaciones cíclicas.
"""
from sqlalchemy.orm import DeclarativeBase

class Base(DeclarativeBase):
    """Base para todos los modelos ORM de SQLAlchemy."""
    pass

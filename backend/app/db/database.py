"""
Base de datos SQLite. Se eligió SQLite (y no Postgres/MySQL) a propósito:
no requiere levantar un servidor de base de datos aparte, el archivo vive
dentro del propio backend, y es perfecto para la idea de "un solo servidor
local del colegio" — cero dependencias externas, todo corre en la misma
máquina.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

from app.core.config import settings

# check_same_thread=False es necesario porque FastAPI puede usar distintos
# threads/tareas async accediendo a la misma conexión SQLite.
engine = create_engine(
    settings.database_url, connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    """Dependency de FastAPI: entrega una sesión de DB y la cierra al terminar."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

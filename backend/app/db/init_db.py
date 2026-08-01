"""
Uso:
    cd backend
    python -m app.db.init_db

Crea el archivo SQLite (app.db) y todas las tablas definidas en models.py,
si no existen todavía. Es seguro correrlo varias veces (no borra datos
existentes, solo crea lo que falte).
"""

from app.db.database import engine, Base
from app.db import models  # noqa: F401  (necesario para registrar los modelos)


def main():
    Base.metadata.create_all(bind=engine)
    print("Tablas creadas/verificadas correctamente en la base de datos.")


if __name__ == "__main__":
    main()

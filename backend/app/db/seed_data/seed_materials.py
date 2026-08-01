"""
Uso:
    cd backend
    python -m app.db.seed_materials

Registra los materiales educativos iniciales en la base de datos. Si el
archivo no existe en `ruta_local`, lo descarga automáticamente desde
`url_web` (la fuente oficial, ej. PeruEduca) y lo guarda ahí.

Esto es lo que permite mantener `storage/materiales/` fuera de git (pesa
mucho) sin perder la capacidad de reconstruir el proyecto desde cero con
un simple `git clone` + este script.
"""

from pathlib import Path

import requests

from app.db.database import SessionLocal
from app.db.models import Material
from app.services.file_utils import asegurar_archivo_local

STORAGE_DIR = Path(__file__).resolve().parent.parent.parent.parent / "storage" / "materiales"

# Agrega aquí cada material que quieras precargar. Cuando tengan más
# grados/materias, solo añaden una entrada más a esta lista.
MATERIALES_INICIALES = [
    {
        "titulo": "Cuadernillo de Matemática - Primer Grado",
        "materia": "matematica",
        "grado": "primaria_primero",
        "tipo": "pdf",
        "ruta_local": str(
            STORAGE_DIR / "primaria_primero" / "matematica"
            / "cuadernillo-matematica-1-2026.pdf"
        ),
        "url_web": (
            "https://repositorio.perueduca.pe/recursos/c-cuadernos-trabajo/"
            "primaria/matematica/cuadernillo-matematica-1-2026.pdf"
        ),
        "fuente": "PeruEduca - Cuaderno de trabajo oficial",
    },
    {
        "titulo": "Cuadernillo de Comunicación - Primer Grado",
        "materia": "comunicacion",
        "grado": "primaria_primero",
        "tipo": "pdf",
        "ruta_local": str(
            STORAGE_DIR / "primaria_primero" / "comunicacion"
            / "cuadernillo-comunicacion-1-2026.pdf"
        ),
        "url_web": "https://repositorios.perueduca.pe/pe-recursos/edures/ce2b24d6-7e5d-44d5-8b0d-6ad4cb2e3cef.pdf",
        "fuente": "PeruEduca - Cuaderno de trabajo oficial",
    },
]

def main():
    db = SessionLocal()
    try:
        for data in MATERIALES_INICIALES:
            existente = (
                db.query(Material)
                .filter_by(titulo=data["titulo"], grado=data["grado"])
                .first()
            )
            if existente:
                print(f"Ya registrado en la BD: {data['titulo']}")
                # Aun así, verifica/descarga el archivo por si falta localmente.
                asegurar_archivo_local(data["ruta_local"], data["url_web"])
                continue

            print(f"Registrando: {data['titulo']}")
            disponible = asegurar_archivo_local(data["ruta_local"], data["url_web"])

            if not disponible:
                print(
                    f"  ⚠ Se registrará en la BD igual, pero sin archivo "
                    f"disponible todavía: {data['titulo']}"
                )

            material = Material(**data)
            db.add(material)

        db.commit()
        print("\nSeed de materiales completado.")
    finally:
        db.close()


if __name__ == "__main__":
    main()
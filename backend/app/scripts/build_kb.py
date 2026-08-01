"""
Uso:
    cd backend
    python -m app.scripts.build_kb

Escanea storage/materiales/<grado>/<materia>/*.pdf, extrae el texto,
lo divide en chunks y construye el índice de búsqueda (TF-IDF) que
usará el chatbot. Vuelve a correr este script cada vez que agregues
o modifiques un PDF.
"""

from app.db.database import SessionLocal
from app.services.knowledge_base import build_index_from_db, INDEX_PATH

def main():
    db = SessionLocal()
    try:
        total = build_index_from_db(db)
    finally:
        db.close()
    
    print(f"\nÍndice construido: {total} fragmentos (chunks) indexados.")
    print(f"Guardado en: {INDEX_PATH}")
    
    if total == 0:
        print(
            "\nNo se genero ningun fragmento. Verifica que:\n"
            "  1. Hayas corrido 'python -m app.db.seed_materials' antes.\n"
            "  2. Los PDFs existan en su 'ruta_local' o tengan un 'url_web' "
            "valido registrado en la tabla materials."
        )


if __name__ == "__main__":
    main()

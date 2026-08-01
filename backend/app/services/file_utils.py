"""Utilidad compartida para garantizar que un archivo local exista,
descargándolo desde una URL web de respaldo si hace falta.

Usado tanto por seed_materials.py (registro inicial) como por build_kb.py
(reconstrucción del índice), para no duplicar la misma lógica.
"""

from pathlib import Path

import requests

_HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; TutorEducativoBot/1.0)"}


def asegurar_archivo_local(ruta_local: str, url_web: str | None) -> bool:
    """Verifica que el archivo exista en `ruta_local`; si no, intenta
    descargarlo desde `url_web`.

    Devuelve True si el archivo está disponible al final, False si no se
    pudo obtener de ninguna forma.
    """
    path = Path(ruta_local)
    if path.exists():
        return True

    if not url_web:
        print(f"  ✗ No existe local y no hay url_web para: {path.name}")
        return False

    print(f"  ⬇ Descargando desde fuente oficial: {url_web}")
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        response = requests.get(url_web, headers=_HEADERS, timeout=30)
        response.raise_for_status()
        path.write_bytes(response.content)
        print(f"  ✓ Descargado correctamente: {path.name}")
        return True
    except requests.RequestException as e:
        print(f"  ✗ Error al descargar {url_web}: {e}")
        return False

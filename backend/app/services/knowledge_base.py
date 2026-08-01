"""
Base de conocimiento construida a partir de los materiales registrados en
la base de datos (tabla `materials`), no escaneando carpetas directamente.

Flujo:
  1. build_index_from_db(db) -> por cada Material en la BD:
       - se asegura que el PDF exista localmente (lo descarga de url_web
         si falta, ver app/services/file_utils.py)
       - extrae el texto con PyMuPDF, lo divide en chunks
       - reemplaza sus MaterialChunk viejos en la BD por los nuevos
     Al final, arma el índice de búsqueda TF-IDF y lo guarda en disco.
  2. load_index() / search(query) -> igual que antes, para el chatbot.

Todo corre local (sin internet) EXCEPTO el paso de descarga, que solo
ocurre una vez durante este preprocesamiento si el archivo aún no existe.
"""

import json
import pickle
from pathlib import Path

import fitz  # PyMuPDF
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from app.db.models import Material, MaterialChunk
from app.services.file_utils import asegurar_archivo_local

MATERIALES_DIR = Path(__file__).resolve().parent.parent.parent / "storage" / "materiales"
INDEX_PATH = Path(__file__).resolve().parent.parent.parent / "storage" / "index" / "kb_index.pkl"

CHUNK_MAX_CHARS = 900
CHUNK_OVERLAP = 150

def _load_topic_map(pdf_path: Path) -> dict:
    """
    Carga un mapeo opcional tema -> [pagina_inicio, pagina_fin] desde un
    archivo .topics.json al lado del PDF. Si no existe, se usa tema "general".
    """
    topics_path = pdf_path.with_suffix("").with_suffix(".topics.json")
    if topics_path.exists():
        with open(topics_path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def _tema_for_page(topic_map: dict, page_num: int) -> str:
    for tema, (inicio, fin) in topic_map.items():
        if inicio <= page_num <= fin:
            return tema
    return "general"


def _split_long_text(texto: str, max_chars: int, overlap: int) -> list[str]:
    """Divide un texto largo en fragmentos con solapamiento, sin cortar
    palabras a la mitad cuando es posible."""
    texto = texto.strip()
    if len(texto) <= max_chars:
        return [texto] if texto else []

    fragments = []
    start = 0
    while start < len(texto):
        end = start + max_chars
        if end < len(texto):
            corte = texto.rfind(" ", start, end)
            if corte != -1 and corte > start:
                end = corte
        fragment = texto[start:end].strip()
        if fragment:
            fragments.append(fragment)
        start = end - overlap if end - overlap > start else end
    return fragments


def build_index_from_db(db, index_path: Path = INDEX_PATH) -> int:
    """Reconstruye los chunks de cada material (desde su PDF) y el índice
    de búsqueda TF-IDF. Devuelve la cantidad total de chunks indexados.

    Debe correrse cada vez que agregas un material nuevo o cambias un PDF.
    """
    materiales = db.query(Material).all()

    if not materiales:
        print("No hay materiales registrados en la BD. Corre primero "
              "seed_materials.py.")
        _guardar_indice_vacio(index_path)
        return 0

    total_chunks_creados = 0

    for material in materiales:
        print(f"Procesando: {material.titulo}")

        disponible = asegurar_archivo_local(material.ruta_local, material.url_web)
        if not disponible:
            print(f"--> Saltando (sin archivo disponible): {material.titulo}")
            continue

        pdf_path = Path(material.ruta_local)
        topic_map = _load_topic_map(pdf_path)

        # Borra los chunks viejos de este material antes de regenerarlos
        db.query(MaterialChunk).filter_by(material_id=material.id).delete()

        doc = fitz.open(pdf_path)
        orden = 0
        for page_index in range(len(doc)):
            page_num = page_index + 1
            texto_pagina = doc[page_index].get_text().strip()
            if not texto_pagina:
                continue

            tema = _tema_for_page(topic_map, page_num)
            fragmentos = _split_long_text(texto_pagina, CHUNK_MAX_CHARS, CHUNK_OVERLAP)

            for fragmento in fragmentos:
                chunk = MaterialChunk(
                    material_id=material.id,
                    tema=tema,
                    pagina=page_num,
                    contenido=fragmento,
                    orden=orden,
                )
                db.add(chunk)
                orden += 1
                total_chunks_creados += 1
        doc.close()

        print(f"  ✓ {orden} fragmentos generados")

    db.commit()

    _reconstruir_indice_busqueda(db, index_path)

    return total_chunks_creados


def _reconstruir_indice_busqueda(db, index_path: Path) -> None:
    """Lee todos los MaterialChunk de la BD (ya actualizados) y arma el
    índice TF-IDF que usa search() para responder rápido en el chat."""

    filas = (
        db.query(MaterialChunk, Material)
        .join(Material, MaterialChunk.material_id == Material.id)
        .all()
    )

    if not filas:
        _guardar_indice_vacio(index_path)
        return

    chunks_info = []
    textos = []
    for chunk, material in filas:
        chunks_info.append(
            {
                "chunk_id": chunk.id,
                "material_id": material.id,
                "titulo": material.titulo,
                "materia": material.materia,
                "grado": material.grado,
                "tema": chunk.tema,
                "pagina": chunk.pagina,
                "archivo": Path(material.ruta_local).name if material.ruta_local else material.titulo,
                "fuente": material.fuente,
                "texto": chunk.contenido,
            }
        )
        textos.append(chunk.contenido)

    vectorizer = TfidfVectorizer(max_features=5000)
    matrix = vectorizer.fit_transform(textos)

    index_path.parent.mkdir(parents=True, exist_ok=True)
    with open(index_path, "wb") as f:
        pickle.dump(
            {"vectorizer": vectorizer, "matrix": matrix, "chunks": chunks_info}, f
        )


def _guardar_indice_vacio(index_path: Path) -> None:
    index_path.parent.mkdir(parents=True, exist_ok=True)
    with open(index_path, "wb") as f:
        pickle.dump({"vectorizer": None, "matrix": None, "chunks": []}, f)


def load_index(index_path: Path = INDEX_PATH) -> dict:
    if not index_path.exists():
        raise FileNotFoundError(
            f"No se encontró el índice en {index_path}. "
            "Corre primero: python -m app.scripts.build_kb"
        )
    with open(index_path, "rb") as f:
        return pickle.load(f)


_cached_index = None

def normalizar_grado(texto: str) -> str:
    """
    Convierte 'Primero de primaria' -> 'primaria_primero'
    """
    partes = texto.lower().split()
    # Asumimos que el formato siempre es "<grado> de <nivel>"
    if len(partes) >= 3 and partes[1] == "de":
        grado = partes[0]       # primero, segundo, tercero...
        nivel = partes[2]       # primaria, secundaria...
        return f"{nivel}_{grado}"
    return texto.lower().replace(" ", "_")

def search(query: str, top_k: int = 3, grado: str | None = None, index_path: Path = INDEX_PATH) -> dict:
    """Busca los chunks más relevantes para una consulta del estudiante.

    Si se especifica `grado`, la búsqueda se limita SOLO a los chunks de
    ese grado. Si no hay ningún material registrado para ese grado (sin
    importar la pregunta), se informa explícitamente en vez de devolver
    contenido de otro nivel.

    Devuelve un dict con:
      - status: "success" | "grado_sin_material" | "not_found"
      - resultados: lista de chunks (solo si status == "success")
    """
    global _cached_index
    if _cached_index is None:
        _cached_index = load_index(index_path)

    vectorizer = _cached_index["vectorizer"]
    matrix = _cached_index["matrix"]
    chunks = _cached_index["chunks"]

    if vectorizer is None or not chunks:
        return {"status": "not_found", "resultados": []}

    # Filtra primero por grado (si se pidió), ANTES de mirar similitud de texto.
    if grado is not None:
        print(grado)
        grado_normalizado = normalizar_grado(grado)
        indices_grado = [i for i, c in enumerate(chunks) if c["grado"] == grado_normalizado]
        if not indices_grado:
            return {"status": "grado_sin_material", "resultados": []}
    else:
        indices_grado = list(range(len(chunks)))

    submatrix = matrix[indices_grado]
    query_vec = vectorizer.transform([query])
    similitudes = cosine_similarity(query_vec, submatrix).flatten()

    orden_local = similitudes.argsort()[::-1][:top_k]
    resultados = []
    for pos in orden_local:
        if similitudes[pos] <= 0:
            continue
        idx_real = indices_grado[pos]
        resultado = dict(chunks[idx_real])
        resultado["score"] = float(similitudes[pos])
        resultados.append(resultado)

    if not resultados:
        return {"status": "not_found", "resultados": []}

    return {"status": "success", "resultados": resultados}

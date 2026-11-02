import pickle

import pytest
from sklearn.feature_extraction.text import TfidfVectorizer

from app.services import knowledge_base as kb


def _chunk(texto, grado="primaria_primero", materia="Matemática"):
    return {"grado": grado, "materia": materia, "texto": texto, "titulo": "Cuadernillo"}


@pytest.fixture()
def index_path(tmp_path):
    chunks = [
        _chunk("Si tienes 6 manzanas y te dan 2 más, tienes 8 manzanas."),
        _chunk("Si tienes 4 lápices y te dan 4 más, tienes 8 lápices."),
        _chunk("Las vocales son a, e, i, o, u.", materia="Comunicación"),
        _chunk("Las fracciones representan partes de un todo.", grado="primaria_quinto"),
    ]
    vectorizer = TfidfVectorizer(token_pattern=r"(?u)\b\w+\b")
    matrix = vectorizer.fit_transform([c["texto"] for c in chunks])
    path = tmp_path / "kb_index.pkl"
    with open(path, "wb") as f:
        pickle.dump({"vectorizer": vectorizer, "matrix": matrix, "chunks": chunks}, f)
    kb._cached_index = None
    yield path
    kb._cached_index = None


def test_single_digits_change_the_result(index_path):
    """Single-digit numbers must count, or '6 más 2' and '4 más 4' look the same."""
    first = kb.search("6 más 2", grado="Primero de primaria", index_path=index_path)
    second = kb.search("4 más 4", grado="Primero de primaria", index_path=index_path)
    assert "6 manzanas" in first["resultados"][0]["texto"]
    assert "4 lápices" in second["resultados"][0]["texto"]


def test_search_stays_in_the_student_grade(index_path):
    result = kb.search("fracciones", grado="Primero de primaria", index_path=index_path)
    assert result["status"] == "not_found"


def test_grade_without_material(index_path):
    result = kb.search("suma", grado="Tercero de primaria", index_path=index_path)
    assert result["status"] == "grado_sin_material"


def test_subject_without_material(index_path):
    result = kb.search(
        "historia", grado="Primero de primaria", materia="Personal Social", index_path=index_path
    )
    assert result["status"] == "materia_sin_material"


def test_split_long_text_keeps_chunks_small_and_overlapping():
    text = " ".join(f"palabra{i}" for i in range(400))
    parts = kb._split_long_text(text, max_chars=200, overlap=40)
    assert len(parts) > 1
    assert all(0 < len(p) <= 200 for p in parts)
    assert parts[0].split()[-1] in parts[1]

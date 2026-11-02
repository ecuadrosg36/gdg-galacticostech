def test_health(client):
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "mode": "local"}


def test_login_creates_student_and_session(client):
    response = client.post(
        "/api/students/login",
        json={"nombre": "Ana Quispe", "grado": "Primero de primaria", "localidad": "Cusco"},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["nombre"] == "Ana Quispe"
    assert body["grado"] == "primaria_primero"
    assert body["chat_session_id"] > 0


def test_login_again_reuses_student_with_new_session(client):
    first = client.post(
        "/api/students/login", json={"nombre": "Ana Quispe", "grado": "Primero de primaria"}
    ).json()
    second = client.post(
        "/api/students/login", json={"nombre": "  ana quispe ", "grado": "Primero de primaria"}
    ).json()
    assert second["id"] == first["id"]
    assert second["chat_session_id"] != first["chat_session_id"]


def test_invalid_grade_is_rejected(client):
    response = client.post(
        "/api/students/login", json={"nombre": "Luis", "grado": "Doctorado"}
    )
    assert response.status_code == 422


def test_update_and_delete_student(client):
    created = client.post(
        "/api/students", json={"nombre": "Rosa", "grado": "Segundo de primaria"}
    ).json()

    updated = client.put(f"/api/students/{created['id']}", json={"localidad": "Puno"})
    assert updated.status_code == 200
    assert updated.json()["localidad"] == "Puno"

    assert client.delete(f"/api/students/{created['id']}").status_code == 204
    assert client.get(f"/api/students/{created['id']}").status_code == 404

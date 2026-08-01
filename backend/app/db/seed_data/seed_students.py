from datetime import datetime

from app.db.database import SessionLocal
from app.db.models import Student

# Lista de estudiantes iniciales
ESTUDIANTES_INICIALES = [
    {
        "nombre": "Ana Torres",
        "grado": "Primero de primaria",
        "localidad": "Cusco",
        "created_at": datetime.utcnow(),
    },
    {
        "nombre": "Luis Fernández",
        "grado": "Segundo de primaria",
        "localidad": "Ayacucho",
        "created_at": datetime.utcnow(),
    },
    {
        "nombre": "María López",
        "grado": "Primero de primaria",
        "localidad": "Puno",
        "created_at": datetime.utcnow(),
    },
]

def main():
    db = SessionLocal()
    try:
        for data in ESTUDIANTES_INICIALES:
            existente = (
                db.query(Student)
                .filter_by(nombre=data["nombre"], grado=data["grado"])
                .first()
            )
            if existente:
                print(f"Ya registrado en la BD: {data['nombre']} ({data['grado']})")
                continue

            print(f"Registrando: {data['nombre']} ({data['grado']})")
            student = Student(**data)
            db.add(student)

        db.commit()
        print("\nSeed de estudiantes completado.")
    finally:
        db.close()


if __name__ == "__main__":
    main()

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.db.models import Student, ChatSession
from app.models.schemas import StudentCreate, StudentUpdate, StudentOut, StudentLoginOut

router = APIRouter(prefix="/api/students", tags=["students"])

@router.post("/login", response_model=StudentLoginOut)
def ingresar_estudiante(data: StudentCreate, db: Session = Depends(get_db)):
    """
    Endpoint para la pantalla de ingreso del estudiante (nombre + grado +
    localidad, sin contraseña). Busca un estudiante existente por nombre y
    grado (sin distinguir mayúsculas/tildes de más o menos espacios); si no
    existe, lo crea.

    Además crea una nueva ChatSession para esta "entrada" a la plataforma,
    y devuelve su id: el frontend debe usar ese id como `session_id` al
    llamar a /api/chat, para que los mensajes queden agrupados y asociados
    correctamente en el historial.
    """
    nombre_normalizado = data.nombre.strip()

    estudiante = (
        db.query(Student)
        .filter(
            func.lower(Student.nombre) == nombre_normalizado.lower(),
            Student.grado == data.grado,
        )
        .first()
    )

    if estudiante:
        # Actualiza localidad por si cambió (ej. familia se mudó)
        if data.localidad and estudiante.localidad != data.localidad:
            estudiante.localidad = data.localidad
            db.commit()
            db.refresh(estudiante)
    else:
        estudiante = Student(
            nombre=nombre_normalizado,
            grado=data.grado,
            localidad=data.localidad,
        )
        db.add(estudiante)
        db.commit()
        db.refresh(estudiante)

    chat_session = ChatSession(student_id=estudiante.id)
    db.add(chat_session)
    db.commit()
    db.refresh(chat_session)

    return StudentLoginOut(
        id=estudiante.id,
        nombre=estudiante.nombre,
        grado=estudiante.grado,
        localidad=estudiante.localidad,
        created_at=estudiante.created_at,
        chat_session_id=chat_session.id,
    )


@router.get("", response_model=list[StudentOut])
def listar_estudiantes(
    grado: str | None = None,
    localidad: str | None = None,
    db: Session = Depends(get_db),
):
    """Lista estudiantes, con filtros opcionales por grado y/o localidad."""
    query = db.query(Student)
    if grado:
        query = query.filter(Student.grado == grado)
    if localidad:
        query = query.filter(Student.localidad == localidad)
    return query.all()


@router.get("/{student_id}", response_model=StudentOut)
def obtener_estudiante(student_id: int, db: Session = Depends(get_db)):
    estudiante = db.query(Student).filter(Student.id == student_id).first()
    if not estudiante:
        raise HTTPException(status_code=404, detail="Estudiante no encontrado")
    return estudiante


@router.post("", response_model=StudentOut, status_code=201)
def crear_estudiante(data: StudentCreate, db: Session = Depends(get_db)):
    estudiante = Student(**data.model_dump())
    db.add(estudiante)
    db.commit()
    db.refresh(estudiante)
    return estudiante


@router.put("/{student_id}", response_model=StudentOut)
def actualizar_estudiante(
    student_id: int, data: StudentUpdate, db: Session = Depends(get_db)
):
    estudiante = db.query(Student).filter(Student.id == student_id).first()
    if not estudiante:
        raise HTTPException(status_code=404, detail="Estudiante no encontrado")

    # Solo actualiza los campos que vinieron en el body (exclude_unset=True)
    for campo, valor in data.model_dump(exclude_unset=True).items():
        setattr(estudiante, campo, valor)

    db.commit()
    db.refresh(estudiante)
    return estudiante


@router.delete("/{student_id}", status_code=204)
def eliminar_estudiante(student_id: int, db: Session = Depends(get_db)):
    estudiante = db.query(Student).filter(Student.id == student_id).first()
    if not estudiante:
        raise HTTPException(status_code=404, detail="Estudiante no encontrado")

    db.delete(estudiante)
    db.commit()
    return None

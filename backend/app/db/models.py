from datetime import datetime

from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    Text,
    DateTime,
    ForeignKey,
    JSON,
)
from sqlalchemy.orm import relationship

from app.db.database import Base


class Teacher(Base):
    __tablename__ = "teachers"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, nullable=False)
    password_hash = Column(String, nullable=False)
    nombre = Column(String, nullable=False)

    materiales = relationship("Material", back_populates="profesor")


class Student(Base):
    __tablename__ = "students"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, nullable=False)
    grado = Column(String, nullable=False)
    localidad = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    quiz_attempts = relationship("QuizAttempt", back_populates="estudiante", cascade="all, delete-orphan")
    chat_sessions = relationship("ChatSession", back_populates="estudiante", cascade="all, delete-orphan")


class Material(Base):
    __tablename__ = "materials"

    id = Column(Integer, primary_key=True, index=True)
    titulo = Column(String, nullable=False)
    materia = Column(String, nullable=False)   # ej. "matematica", "comunicacion"
    grado = Column(String, nullable=False)     # ej. "primaria_primero"
    tipo = Column(String, default="pdf")       # "pdf", "imagen", "video"

    # Doble referencia: dónde vive el archivo localmente, y de dónde se
    # puede descargar si no está presente (ej. tras un clone del repo,
    # sin necesidad de subir el PDF pesado a GitHub).
    ruta_local = Column(String, nullable=True)
    url_web = Column(String, nullable=True)

    fuente = Column(String, nullable=True)     # ej. "PeruEduca - Cuadernillo oficial"
    uploaded_by = Column(Integer, ForeignKey("teachers.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    profesor = relationship("Teacher", back_populates="materiales")
    chunks = relationship("MaterialChunk", back_populates="material")
    quizzes = relationship("Quiz", back_populates="material")


class MaterialChunk(Base):
    __tablename__ = "material_chunks"

    id = Column(Integer, primary_key=True, index=True)
    material_id = Column(Integer, ForeignKey("materials.id"), nullable=False)
    tema = Column(String, default="general")
    pagina = Column(Integer, nullable=True)
    contenido = Column(Text, nullable=False)
    orden = Column(Integer, default=0)

    material = relationship("Material", back_populates="chunks")


class Quiz(Base):
    __tablename__ = "quizzes"

    id = Column(Integer, primary_key=True, index=True)
    material_id = Column(Integer, ForeignKey("materials.id"), nullable=False)
    preguntas = Column(JSON, nullable=False)  # lista de {pregunta, opciones, correcta}

    material = relationship("Material", back_populates="quizzes")
    intentos = relationship("QuizAttempt", back_populates="quiz", cascade="all, delete-orphan")


class QuizAttempt(Base):
    __tablename__ = "quiz_attempts"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    quiz_id = Column(Integer, ForeignKey("quizzes.id"), nullable=False)
    score = Column(Float, nullable=False)
    respuestas = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    estudiante = relationship("Student", back_populates="quiz_attempts")
    quiz = relationship("Quiz", back_populates="intentos")


class ChatSession(Base):
    __tablename__ = "chat_sessions"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    estudiante = relationship("Student", back_populates="chat_sessions")
    mensajes = relationship("ChatMessage", back_populates="sesion", cascade="all, delete-orphan")


class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("chat_sessions.id"), nullable=False)
    role = Column(String, nullable=False)  # "user" | "assistant"
    content = Column(Text, nullable=False)
    tema = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    sesion = relationship("ChatSession", back_populates="mensajes")

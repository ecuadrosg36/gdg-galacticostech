from datetime import datetime
from pydantic import BaseModel, ConfigDict, field_validator
from typing import List, Optional
from app.core.grados import es_grado_valido, GRADOS, normalizar_grado


def _validar_grado(v: str | None) -> str | None:
    if v is not None and not es_grado_valido(v):
        opciones = ", ".join(GRADOS.keys())
        raise ValueError(f"grado inválido: '{v}'. Debe ser uno de: {opciones}")
    return v


class StudentBase(BaseModel):
    nombre: str
    grado: str
    localidad: str | None = None

    @field_validator("grado")
    @classmethod
    def validar_grado(cls, v):
        return _validar_grado(normalizar_grado(v))


class StudentCreate(StudentBase):
    pass


class StudentUpdate(BaseModel):
    """Todos los campos opcionales: solo se actualiza lo que se envíe."""
    nombre: str | None = None
    grado: str | None = None
    localidad: str | None = None

    @field_validator("grado")
    @classmethod
    def validar_grado(cls, v):
        return _validar_grado(v)


class StudentOut(StudentBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime


class StudentLoginOut(StudentOut):
    """Respuesta del endpoint de ingreso: incluye el chat_session_id que
    el frontend debe usar para las siguientes llamadas a /api/chat."""
    chat_session_id: int


class ChatRequest(BaseModel):
    student_id: int
    session_id: int
    message: str

class ChatResponse(BaseModel):
    reply: str
    mode: str
    tema: Optional[str] = None

class ChatMessageBase(BaseModel):
    role: str
    content: str
    tema: Optional[str] = None

class ChatMessageResponse(ChatMessageBase):
    id: int
    session_id: int
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

class ChatSessionCreate(BaseModel):
    student_id: int

class ChatSessionResponse(BaseModel):
    id: int
    student_id: int
    created_at: datetime
    mensajes: List[ChatMessageResponse] = []
    model_config = ConfigDict(from_attributes=True)
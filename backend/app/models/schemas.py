from datetime import datetime
from pydantic import BaseModel, ConfigDict


class StudentBase(BaseModel):
    nombre: str
    grado: str
    localidad: str | None = None


class StudentCreate(StudentBase):
    pass


class StudentUpdate(BaseModel):
    """Todos los campos opcionales: solo se actualiza lo que se envíe."""
    nombre: str | None = None
    grado: str | None = None
    localidad: str | None = None


class StudentOut(StudentBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime

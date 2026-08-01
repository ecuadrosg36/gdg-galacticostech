from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from google.genai import types

from app.agents.tutor_agent import root_agent
from app.core.config import settings
from app.db.database import get_db
from app.db.models import Student
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService

router = APIRouter(prefix="/api/chat", tags=["chat"])

# NOTA para el MVP: sesiones en memoria (se pierden al reiniciar el server).
# Para producción real, cambiar a un SessionService persistente.
_session_service = InMemorySessionService()
_runner = Runner(
    agent=root_agent, app_name=settings.app_name, session_service=_session_service
)


class ChatRequest(BaseModel):
    student_id: int
    session_id: str
    message: str


class ChatResponse(BaseModel):
    reply: str
    mode: str


@router.post("", response_model=ChatResponse)
async def chat(payload: ChatRequest, db: Session = Depends(get_db)) -> ChatResponse:
    estudiante = db.query(Student).filter(Student.id == payload.student_id).first()
    if not estudiante:
        raise HTTPException(status_code=404, detail="Estudiante no encontrado")

    user_id = str(estudiante.id)

    # Crea la sesión con el grado del estudiante ya en el estado, para que
    # la tool "buscar_material" lo lea vía ToolContext sin que el modelo
    # tenga que adivinarlo ni pasarlo como argumento.
    try:
        await _session_service.create_session(
            app_name=settings.app_name,
            user_id=user_id,
            session_id=payload.session_id,
            state={"grado": estudiante.grado},
        )
    except Exception:
        pass  # la sesión ya existía, seguimos usándola

    contenido = types.Content(role="user", parts=[types.Part(text=payload.message)])

    respuesta_final = ""
    async for event in _runner.run_async(
        user_id=user_id,
        session_id=payload.session_id,
        new_message=contenido,
    ):
        if event.is_final_response() and event.content and event.content.parts:
            textos = [
                p.text
                for p in event.content.parts
                if getattr(p, "text", None) and not getattr(p, "thought", False)
            ]
            if textos:
                respuesta_final = "\n".join(textos)

    return ChatResponse(reply=respuesta_final, mode=settings.mode)

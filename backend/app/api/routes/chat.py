from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, ConfigDict
from typing import List, Optional
from datetime import datetime
from google.genai import types

# Importes de tu proyecto
from app.agents.tutor_agent import root_agent
from app.core.config import settings
from app.db.database import get_db
from app.db.models import Student, ChatSession, ChatMessage
from app.models.schemas import ChatRequest, ChatResponse, ChatMessageBase, ChatMessageResponse, ChatSessionCreate, ChatSessionResponse
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService

router = APIRouter(prefix="/api/chat", tags=["Chat & Sessions"])

# ==========================================
# Configuración ADK (MVP)
# ==========================================
# NOTA para el MVP: sesiones en memoria (se pierden al reiniciar el server).
# Para producción real, cambiar a un SessionService persistente.
_session_service = InMemorySessionService()
_runner = Runner(
    agent=root_agent, app_name=settings.app_name, session_service=_session_service
)

# ==========================================
# ENDPOINTS DE SESIONES Y DASHBOARD
# ==========================================

@router.post("/sessions", response_model=ChatSessionResponse, status_code=status.HTTP_201_CREATED)
def create_chat_session(session: ChatSessionCreate, db: Session = Depends(get_db)):
    """Crea una nueva sesión de chat vacía para un estudiante."""
    student = db.query(Student).filter(Student.id == session.student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Estudiante no encontrado")
        
    db_session = ChatSession(student_id=session.student_id)
    db.add(db_session)
    db.commit()
    db.refresh(db_session)
    return db_session

@router.get("/sessions", response_model=List[ChatSessionResponse])
def get_chat_sessions(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Obtiene todas las sesiones (Útil para el dashboard del profesor)."""
    return db.query(ChatSession).offset(skip).limit(limit).all()

@router.get("/sessions/{session_id}/messages", response_model=List[ChatMessageResponse])
def get_session_messages(session_id: int, db: Session = Depends(get_db)):
    """Obtiene el historial de una sesión específica para sincronización."""
    messages = db.query(ChatMessage).filter(ChatMessage.session_id == session_id).order_by(ChatMessage.created_at.asc()).all()
    return messages

# ==========================================
# ENDPOINT PRINCIPAL CON GOOGLE ADK
# ==========================================

@router.post("/send", response_model=ChatResponse)
async def chat_with_adk(payload: ChatRequest, db: Session = Depends(get_db)) -> ChatResponse:
    """Envía un mensaje al modelo Gemma/Gemini orquestado por ADK y guarda el historial."""
    estudiante = db.query(Student).filter(Student.id == payload.student_id).first()
    if not estudiante:
        raise HTTPException(status_code=404, detail="Estudiante no encontrado")

    chat_session = (
        db.query(ChatSession)
        .filter(
            ChatSession.id == payload.session_id,
            ChatSession.student_id == estudiante.id,
        )
        .first()
    )
    if not chat_session:
        raise HTTPException(
            status_code=404,
            detail="session_id no encontrado para este estudiante. "
            "¿Llamaste primero a POST /api/chat/sessions?",
        )

    user_id = str(estudiante.id)
    adk_session_id = str(chat_session.id)

    # Inyectar contexto educativo en la memoria del agente ADK
    try:
        await _session_service.create_session(
            app_name=settings.app_name,
            user_id=user_id,
            session_id=adk_session_id,
            state={"grado": estudiante.grado},
        )
    except Exception:
        pass  # la sesión ya existía, seguimos usándola

    contenido = types.Content(role="user", parts=[types.Part(text=payload.message)])
    
    respuesta_final = ""
    async for event in _runner.run_async(
        user_id=user_id,
        session_id=adk_session_id,
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

    sesion_adk = await _session_service.get_session(
        app_name=settings.app_name, user_id=user_id, session_id=adk_session_id
    )
    tema_detectado = sesion_adk.state.get("ultimo_tema") if sesion_adk else None
    # Si el LLM respondió directamente sin usar la tool, no hay tema del MINEDU
    if not tema_detectado:
        tema_detectado = "charla_general"

    # Guardar persistencia en BD Relacional (SQLAlchemy)
    db.add(ChatMessage(session_id=chat_session.id, role="user", content=payload.message))
    db.add(
        ChatMessage(
            session_id=chat_session.id,
            role="assistant",
            content=respuesta_final,
            tema=tema_detectado,
        )
    )
    db.commit()

    return ChatResponse(reply=respuesta_final, mode=settings.mode, tema=tema_detectado)
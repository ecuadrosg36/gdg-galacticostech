from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import chat, students
from app.core.config import settings

app = FastAPI(title=settings.app_name)

origenes_permitidos = [origen.strip() for origen in settings.cors_origins.split(",")]
# En desarrollo, permitir el origen de Angular (ng serve, puerto 4200).
# En producción, restringir a la URL real del frontend deployado.
app.add_middleware(
    CORSMiddleware,
    allow_origins=origenes_permitidos,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chat.router)
app.include_router(students.router)


@app.get("/api/health")
def health():
    return {"status": "ok", "mode": settings.mode}

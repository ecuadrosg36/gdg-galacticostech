"""
Script de prueba rápida del agente tutor, por consola.

Uso:
    cd backend
    python -m app.agents.test_local

Asegúrate de tener Ollama corriendo (`ollama serve`) y el modelo descargado
(`ollama pull gemma4:e2b`) si MODE=local en tu .env.
"""

import asyncio

from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

from app.agents.tutor_agent import root_agent
from app.core.config import settings

APP_NAME = settings.app_name
USER_ID = "estudiante_demo"
SESSION_ID = "sesion_demo_1"


async def preguntar(runner: Runner, texto: str) -> str:
    contenido = types.Content(role="user", parts=[types.Part(text=texto)])

    respuesta_final = ""
    async for event in runner.run_async(
        user_id=USER_ID, session_id=SESSION_ID, new_message=contenido
    ):
        if event.is_final_response() and event.content and event.content.parts:
            #respuesta_final = event.content.parts[0].text
            respuesta_final = event.content.parts[-1].text

    return respuesta_final


async def main():
    session_service = InMemorySessionService()
    await session_service.create_session(
        app_name=APP_NAME, user_id=USER_ID, session_id=SESSION_ID
    )

    runner = Runner(
        agent=root_agent,
        app_name=APP_NAME,
        session_service=session_service,
    )

    print(f"--- Tutor educativo (modo: {settings.mode}) ---")
    print("Escribe tu pregunta (o 'salir' para terminar)\n")

    while True:
        pregunta = input("Estudiante: ").strip()
        if pregunta.lower() in ("salir", "exit", "quit"):
            break
        if not pregunta:
            continue

        respuesta = await preguntar(runner, pregunta)
        print(f"Tutor: {respuesta}\n")


if __name__ == "__main__":
    asyncio.run(main())

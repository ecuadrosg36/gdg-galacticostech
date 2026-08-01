"""
Tool del agente ADK: busca material educativo en la base de conocimiento
construida localmente a partir de los PDFs.

IMPORTANTE: el grado del estudiante NO se le pide a Gemma como argumento
(el modelo no tiene forma confiable de saberlo). En cambio, se inyecta
automáticamente vía ToolContext, a partir del estado de la sesión que el
backend define al crear la sesión de chat (ver app/api/routes/chat.py).
"""

from google.adk.tools import ToolContext

from app.services import knowledge_base

def buscar_material(consulta: str, tool_context: ToolContext) -> dict:
    """Busca en el material educativo local (extraído de los cuadernillos PDF)
    fragmentos relevantes para responder la pregunta del estudiante.

    Args:
        consulta (str): la pregunta o tema que el estudiante quiere aprender,
            por ejemplo "¿qué es una fracción?" o "sumas con llevada".

    Returns:
        dict: status y datos según el caso:
          - "success": hay fragmentos relevantes en "fragmentos".
          - "grado_sin_material": no hay NINGÚN material cargado para el
            grado de este estudiante todavía (independiente de la pregunta).
          - "not_found": sí hay material para su grado, pero nada relevante
            para esta pregunta en particular.
    """
    grado_estudiante = tool_context.state.get("grado")

    resultado = knowledge_base.search(consulta, top_k=3, grado=grado_estudiante)

    if resultado["status"] == "grado_sin_material":
        return {
            "status": "grado_sin_material",
            "message": (
                f"Todavía no hay material educativo cargado para el grado "
                f"'{grado_estudiante}'. Avísale a tu profesor."
            ),
        }

    if resultado["status"] == "not_found":
        return {
            "status": "not_found",
            "message": f"No se encontró material relacionado con: '{consulta}'.",
        }

    return {
        "status": "success",
        "fragmentos": [
            {
                "texto": r["texto"],
                "tema": r["tema"],
                "materia": r["materia"],
                "grado": r["grado"],
                "fuente": f"{r['archivo']}, página {r['pagina']}",
            }
            for r in resultado["resultados"]
        ],
    }

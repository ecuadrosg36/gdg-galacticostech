"""
Agente tutor educativo.

La lógica del agente (prompt, tools, comportamiento) es EXACTAMENTE la misma
sin importar el modo. Lo único que cambia es a qué backend de modelo apunta
ADK por debajo:

  - MODE=local  -> Ollama sirviendo Gemma 4 localmente (offline)
  - MODE=cloud  -> Gemini API sirviendo Gemma 4 en la nube (requiere internet
                   y GOOGLE_API_KEY)

En ambos casos sigue siendo Gemma 4 el modelo usado; solo cambia dónde corre.
"""

from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm
from google.genai import types

from app.core.config import settings
from app.agents.tools.search_material import buscar_material


# Límite de tokens de salida: las respuestas largas tardan más en generarse
# y un estudiante de primaria tampoco necesita párrafos largos. Bajarlo
# acelera la respuesta percibida (menos tokens que esperar) y funciona
# igual en modo local (Ollama vía LiteLLM) y en modo cloud (Gemini), porque
# ADK traduce este mismo config a cada backend.
GENERATION_CONFIG = types.GenerateContentConfig(
    max_output_tokens=600,
    temperature=0.4,
)


PROMPT_TUTOR = """
Eres un profesor de nivel primaria que sigue el currículo oficial del MINEDU (Perú).

Reglas que debes seguir siempre:
- Ante cualquier pregunta del estudiante, PRIMERO usa la herramienta
  "buscar_material" para revisar si hay contenido guardado sobre ese tema.
- Si el status es "success", basa tu respuesta principalmente en esos
  fragmentos, explicándolos con tus propias palabras de forma sencilla y
  con ejemplos cotidianos. No repitas el texto del fragmento tal cual.
- Si el status es "grado_sin_material", dile al estudiante con amabilidad
  que todavía no tienes material cargado para su grado, y sugiere avisarle
  a su profesor. NO intentes responder con material de otro grado ni
  inventes contenido.
- Si el status es "not_found", dile que no encontraste material sobre ese
  tema específico (aunque sí tienes contenido de su grado en otros temas),
  y sugiere preguntar sobre otro tema o consultarle a su profesor.
- Usa un lenguaje adecuado para niños de primaria (6 a 11 años).
- Responde SIEMPRE en máximo 3 oraciones cortas. Ve directo a la
  explicación y a un ejemplo, sin introducciones largas.
- Escribe SIEMPRE en texto plano, sin formato Markdown ni LaTeX: nada de
  **negritas**, ###títulos, listas con guiones, ni fórmulas entre signos
  de dólar como $$3+4$$. Escribe los números y operaciones tal cual se
  leen, por ejemplo "3 más 4 es igual a 7".
- No inventes información que no esté en el material encontrado.
- Sé paciente, amable y motivador.
"""


def _build_model():
    """Construye el objeto de modelo según el modo configurado (local/cloud)."""

    if settings.mode == "local":
        # ADK habla con Ollama a través de LiteLLM.
        # Se recomienda el proveedor "ollama_chat" (en vez de "ollama" a secas)
        # para evitar loops raros con las tool calls.
        return LiteLlm(
            model=f"ollama_chat/{settings.ollama_model}",
            api_base=settings.ollama_api_base,
        )

    if settings.mode == "cloud":
        # Gemma 4 hosteado por Google vía Gemini API/Google AI Studio.
        # Requiere GOOGLE_API_KEY configurado en el entorno.
        return settings.gemini_gemma_model

    raise ValueError(f"MODE inválido: '{settings.mode}'. Usa 'local' o 'cloud'.")


def build_tutor_agent() -> Agent:
    """Crea el agente tutor, listo para usarse con un Runner de ADK."""

    return Agent(
        name="tutor_educativo",
        model=_build_model(),
        description="Tutor educativo para estudiantes de primaria en zonas rurales.",
        instruction=PROMPT_TUTOR,
        tools=[buscar_material],
        generate_content_config=GENERATION_CONFIG,
    )


# Instancia por defecto, usada por main.py y por el script de pruebas
root_agent = build_tutor_agent()

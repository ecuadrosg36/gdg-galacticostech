# Build with Gemma - GDG Lima
## Galácticos Tech — Tutor Educativo Offline con IA para zonas rurales del Perú

> Build with Gemma - AI Competition | Track: **Local AI & Edge Intelligence**

## 🎯 Propuesta

En muchas zonas rurales del Perú, el acceso a internet es limitado o inexistente, lo que
restringe severamente el acceso de niños de nivel primario a materiales de apoyo educativo,
tutorías o resolución de dudas fuera del horario de clase. La paradoja actual es que, aunque
la IA puede resolver la educación personalizada, asume un privilegio inexistente en la
realidad rural: la conectividad constante.

**Galácticos Tech** resuelve este problema democratizando el acceso a la educación mediante
una plataforma que corre **Gemma 4 completamente local** a través de una arquitectura de
**Servidor Edge Comunitario**.

El sistema se instala en la computadora central de un Centro de Acceso Digital (o laboratorio
del colegio). Los estudiantes asisten y utilizan sus celulares básicos para conectarse a la
red WiFi local (intranet), accediendo a un tutor inteligente sin consumir un solo megabyte de
datos de internet.

## 🌍 ODS y Track

- **Track:** Local AI & Edge Intelligence
- **ODS:** 4 (Educación de Calidad) y 10 (Reducción de las Desigualdades)

## 📚 Fuentes de conocimiento

- Currículo Nacional y cuadernillos de [MINEDU](https://www.gob.pe/minedu) /
  [Perú Educa](https://www.perueduca.pe/), usados para alimentar el motor RAG offline. Cada
  material queda registrado con una `ruta_local` y una `url_web` de respaldo (la fuente
  oficial), de modo que si el PDF no está presente en el servidor, el sistema puede
  descargarlo una sola vez durante el preprocesamiento (nunca durante el chat en vivo).
- Datos abiertos de infraestructura educativa (conectividad rural) del
  [Portal de Datos Abiertos del Estado Peruano](https://www.datosabiertos.gob.pe/).

## 🏗️ Arquitectura y Tecnologías

El proyecto funciona con una arquitectura centralizada 100% offline. El frontend se
construye en CSS plano, sin dependencias de CDNs externos, para garantizar que la UI cargue
correctamente incluso sin conexión a internet.

```
┌─────────────────────────────────────────────┐
│          Dispositivos Móviles Básicos        │
│    (Navegador Web del celular del alumno)    │
└───────────────────┬───────────────────────────┘
                    │  HTTP (Frontend / API)
                    │  Intranet Local (Sin Internet)
                    ▼
┌─────────────────────────────────────────────┐
│       Servidor Edge (Centro de Acceso)        │
│                                                │
│  [ UI: Angular ]         [ API: FastAPI ]     │
│                                                │
│  ┌──────────────┐        ┌────────────────┐  │
│  │  Google ADK   │───────▶│     Ollama      │  │
│  │ (Orquestador  │        │ (Gemma 4 Local) │  │
│  │  y Agentes,   │        │  modo "local"   │  │
│  │  ToolContext) │        └────────────────┘  │
│  └──────┬────────┘                            │
│         │                ┌────────────────┐   │
│         │                │  Gemini API     │   │
│         ├───────────────▶│ (Gemma 4 cloud, │   │
│         │                │  modo "cloud")  │   │
│         │                └────────────────┘   │
│         │                                     │
│         ▼                                     │
│  ┌──────────────────────────────────────┐    │
│  │   Base de datos (SQLite/SQLAlchemy)   │    │
│  │  Students · Teachers · Materials ·    │    │
│  │  MaterialChunks · ChatSessions ·      │    │
│  │  ChatMessages (con tema) · Quizzes    │    │
│  └───────────────┬──────────────────────┘    │
│                  │                            │
│                  ▼                            │
│  ┌──────────────────────────────────────┐    │
│  │  Índice de búsqueda RAG (TF-IDF,      │    │
│  │  scikit-learn) — reconstruido a       │    │
│  │  partir de los MaterialChunks         │    │
│  └──────────────────────────────────────┘    │
└─────────────────────────────────────────────┘
```

**El modelo (Gemma 4) es el mismo en ambos modos** — lo único que cambia es dónde corre:
`ollama_chat/gemma4:e2b` en modo local, o `gemma-4-4b-it` vía la API de Gemini en modo cloud
(útil como respaldo si el hardware disponible es más limitado, o durante desarrollo).

| Componente | Tecnología |
|---|---|
| Frontend | Angular (UI en CSS plano, sin CDNs externos) |
| Backend / API | Python + FastAPI |
| Orquestación del agente | Google ADK (con `ToolContext` para pasar contexto de sesión) |
| Modelo LLM | Gemma 4 (local vía Ollama, o cloud vía Gemini API) |
| Base de datos | SQLite + SQLAlchemy |
| Búsqueda / RAG | scikit-learn (TF-IDF) sobre chunks extraídos con PyMuPDF |
| Control de versiones | GitHub |

## 🧩 Módulos y Flujo del Sistema

### MVP actual (Hackathon Sprint)

1. **Ingreso del estudiante** (`POST /api/students/ingresar`): el estudiante escribe su
   nombre y selecciona su grado (y localidad). El backend busca si ya existe un registro
   igual (sin distinguir mayúsculas ni espacios) y lo reutiliza; si no, lo crea. Cada ingreso
   genera una nueva `ChatSession`.
2. **Chat con Gemma** (`POST /api/chat`): interfaz conversacional orquestada por ADK, que
   adapta el lenguaje a un niño de primaria. El grado del estudiante se inyecta en el estado
   de la sesión (vía `ToolContext`), así la búsqueda de material **solo considera contenido
   de su propio grado** — si no hay material cargado para ese grado, el tutor lo informa
   claramente en vez de responder con contenido de otro nivel.
3. **Material educativo (RAG)**: los cuadernillos del MINEDU se registran en la tabla
   `materials` (con `ruta_local` y `url_web`), se procesan con PyMuPDF, se dividen en
   fragmentos (`material_chunks`) y se indexan con TF-IDF. Ante una duda, el agente busca el
   contexto localmente antes de responder, evitando alucinaciones.
4. **Persistencia de conversación y tema**: cada intercambio (pregunta del
   estudiante + respuesta del tutor) se guarda en `chat_messages`, junto con el **tema**
   detectado en el material usado para responder. Esto ya deja lista la data para el futuro
   dashboard docente (ej. "qué temas pregunta más cada estudiante").
5. **CRUD de estudiantes** (`GET/POST/PUT/DELETE /api/students`): gestión administrativa
   básica, con validación de que el `grado` sea uno de los valores oficiales reconocidos
   (evita inconsistencias como comparar `"Primero de primaria"` contra `"primaria_primero"`).

### Roadmap (futuras implementaciones)

- **Quizzes**: evaluaciones cortas al final de cada tema para medir retención.
- **Recomendaciones**: motor de sugerencias basado en el historial de temas ya consultados
  (la tabla `chat_messages.tema` ya provee la data base para esto).
- **Dashboard para profesores**: panel de monitoreo por estudiante y por tema (temas más
  consultados, en cuáles se traba cada alumno), con sincronización a la nube cuando el
  colegio recupera conectividad.
- **Subida de materiales por el profesor**: mismo pipeline de extracción/indexado, expuesto
  como endpoint de carga de archivos.

## ⚠️ Limitaciones conocidas

Documentadas a propósito, como parte de las decisiones de ingeniería del sprint:

- **Búsqueda TF-IDF sin stemming**: al comparar texto exacto, preguntas con plurales o
  conjugaciones distintas al material original (ej. "triángulos" vs "triángulo") pueden no
  encontrar coincidencia. Mejora futura: aplicar un stemmer en español antes de indexar.
- **El índice de búsqueda se cachea en memoria del proceso**: si reconstruyes el índice
  (`build_kb.py`) mientras el backend sigue corriendo, los cambios no se reflejan hasta
  reiniciar el servidor.
- **Manejo de errores parcial en el indexado**: si un material no tiene `ruta_local` ni
  `url_web` válidos, o su PDF está corrupto, la reconstrucción del índice puede fallar por
  completo en vez de saltar solo ese material (pendiente de aislar con manejo de errores por
  material).

## 🚀 Cómo correr el proyecto localmente (Demo End-to-End)

### 1. Preparar el modelo local (Ollama)

```bash
ollama pull gemma4:e2b
```

### 2. Levantar el backend (FastAPI)

```bash
cd backend
python -m venv venv

# Activar entorno (Windows)
venv\Scripts\activate
# Activar entorno (Mac/Linux)
source venv/bin/activate

pip install -r requirements.txt

# Configurar entorno
cp .env.example .env

# Inicializar base de datos y cargar datos base
python -m app.db.init_db
python -m app.db.seed_students
python -m app.db.seed_materials
python -m app.scripts.build_kb

# Levantar servidor
uvicorn app.main:app --port 8000
```

Verifica que el backend responde en: `http://localhost:8000/api/health`

### 3. Levantar el frontend (Angular)

En una nueva terminal:

```bash
cd frontend
npm install
ng serve
```

Abre `http://localhost:4200` en tu navegador.

### Para probar

1. Ingresa con un estudiante de prueba (ej. "Ana Torres", Primero de primaria) — si no
   existe, se crea automáticamente al ingresar.
2. Escribe una pregunta de matemática básica y confirma que Gemma genera la respuesta
   consumiendo el contenido oficial del MINEDU, de forma 100% offline (modo local).
3. Repite la pregunta con un estudiante de un grado sin material cargado, y confirma que el
   tutor lo informa claramente en vez de responder con contenido de otro nivel.

## 📋 Pendientes / decisiones abiertas

- [ ] Aislar errores por material en `build_index_from_db` (try/except individual + commit
      progresivo)
- [ ] Endpoint para invalidar/recargar el índice en memoria sin reiniciar el servidor
- [ ] Stemming en español para mejorar la búsqueda TF-IDF
- [ ] Dashboard docente (consumiendo `chat_messages.tema` ya disponible)
- [ ] Endpoint de subida de materiales para profesores

// Modelo principal del Estudiante (StudentOut)
export interface Student {
  id: number;
  nombre: string;
  grado: string;
  localidad?: string;
  created_at: string;
}

// Datos para crear un estudiante o hacer login (StudentCreate)
export interface StudentCreate {
  nombre: string;
  grado: string;
  localidad?: string;
}

// Datos para actualizar (StudentUpdate) - Todos opcionales
export interface StudentUpdate {
  nombre?: string;
  grado?: string;
  localidad?: string;
}

// Respuesta del login (ya la tenías, la pongo como referencia)
export interface StudentLoginResponse {
  id: number;
  nombre: string;
  grado: string;
  localidad?: string;
  created_at: string;
  chat_session_id: number;
}

// --- Chat ---
export interface ChatMessageRequest {
  student_id: number;
  session_id: number;
  message: string;
  materia?: string;
}

export interface ChatResponse {
  reply: string;
  mode: string;
  tema: string | null;
}

// Para el historial (Dashboard o recargar la página)
export interface ChatMessage {
  id: number;
  session_id: number;
  role: 'user' | 'assistant';
  content: string;
  tema: string | null;
  created_at: string;
}
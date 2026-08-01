import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { 
  StudentCreate, 
  StudentLoginResponse, 
  ChatMessageRequest, 
  ChatResponse,
  ChatMessage
} from '../models/api.models';
import { environment } from '../environments/environment';

@Injectable({
  providedIn: 'root'
})
export class TutorService {
  // Ajusta el puerto si tu backend corre en otro distinto
  private apiUrl = `${environment.apiUrl}/api`;

  constructor(private http: HttpClient) {}

  /**
   * Paso 1: Ingresar a la plataforma
   * Llama a POST /api/students/login
   */

  /**
   * Paso 2: Hablar con Gemma
   * Llama a POST /api/chat/send
   */
  sendMessage(data: ChatMessageRequest): Observable<ChatResponse> {
    return this.http.post<ChatResponse>(`${this.apiUrl}/chat/send`, data);
  }

  /**
   * Paso 3: Obtener historial (Opcional, para el dashboard o recargar el chat)
   * Llama a GET /api/chat/sessions/{id}/messages
   */
  getSessionHistory(sessionId: number): Observable<ChatMessage[]> {
    return this.http.get<ChatMessage[]>(`${this.apiUrl}/chat/sessions/${sessionId}/messages`);
  }
}
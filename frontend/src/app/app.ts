import { Component, signal } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { HttpClient } from '@angular/common/http';

import { environment } from '../environments/environment';

interface ChatMessage {
  role: 'student' | 'gemma';
  text: string;
}

interface ChatResponse {
  reply: string;
  mode: string;
}

@Component({
  selector: 'app-root',
  imports: [FormsModule],
  templateUrl: './app.html',
  styleUrl: './app.css'
})
export class App {
  protected readonly studentId = 1; // Ana Torres - Primero de primaria (Cusco)
  protected readonly sessionId = crypto.randomUUID();

  protected readonly messages = signal<ChatMessage[]>([
    { role: 'gemma', text: 'Hola, soy Gemma. Pregúntame lo que quieras sobre matemática de primer grado.' }
  ]);
  protected readonly draft = signal('');
  protected readonly loading = signal(false);
  protected readonly mode = signal<string | null>(null);

  constructor(private readonly http: HttpClient) {}

  enviar(): void {
    const texto = this.draft().trim();
    if (!texto || this.loading()) {
      return;
    }

    this.messages.update((msgs) => [...msgs, { role: 'student', text: texto }]);
    this.draft.set('');
    this.loading.set(true);

    this.http
      .post<ChatResponse>(`${environment.apiUrl}/api/chat`, {
        student_id: this.studentId,
        session_id: this.sessionId,
        message: texto
      })
      .subscribe({
        next: (res) => {
          this.mode.set(res.mode);
          this.messages.update((msgs) => [...msgs, { role: 'gemma', text: res.reply }]);
          this.loading.set(false);
        },
        error: () => {
          this.messages.update((msgs) => [
            ...msgs,
            { role: 'gemma', text: 'No pude conectarme con el tutor. Verifica que el backend y Ollama estén corriendo.' }
          ]);
          this.loading.set(false);
        }
      });
  }
}

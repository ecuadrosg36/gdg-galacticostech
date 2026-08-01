import { Component, signal } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { HttpClient } from '@angular/common/http';

import { environment } from '../../../environments/environment';

interface ChatMessage {
  role: 'student' | 'gemma';
  text: string;
}

interface ChatResponse {
  reply: string;
  mode: string;
}

interface Student {
  id: number;
  nombre: string;
  grado: string;
}

@Component({
  selector: 'app-chat',
  standalone: true,
  imports: [FormsModule],
  templateUrl: './chat.html',
  styleUrl: './chat.css'
})
export class Chat {
  protected readonly sessionId = crypto.randomUUID();

  protected readonly grados = [
    'Primero de primaria',
    'Segundo de primaria',
    'Tercero de primaria'
  ];

  // Identificación del estudiante (no es login/autenticación: sin contraseña,
  // solo nombre + grado, apropiado para niños de primaria).
  protected readonly student = signal<Student | null>(null);
  protected readonly nombreInput = signal('');
  protected readonly gradoInput = signal(this.grados[0]);
  protected readonly startError = signal<string | null>(null);
  protected readonly startLoading = signal(false);

  protected readonly messages = signal<ChatMessage[]>([]);
  protected readonly draft = signal('');
  protected readonly loading = signal(false);
  protected readonly mode = signal<string | null>(null);

  constructor(private readonly http: HttpClient) {}

  comenzar(): void {
    const nombre = this.nombreInput().trim();
    if (!nombre || this.startLoading()) {
      return;
    }

    this.startLoading.set(true);
    this.startError.set(null);

    this.http
      .post<Student>(`${environment.apiUrl}/api/students`, {
        nombre,
        grado: this.gradoInput()
      })
      .subscribe({
        next: (res) => {
          this.student.set(res);
          this.messages.set([
            { role: 'gemma', text: `Hola, ${res.nombre.split(' ')[0]}. Soy Gemma. Pregúntame lo que quieras sobre matemática.` }
          ]);
          this.startLoading.set(false);
        },
        error: () => {
          this.startError.set('No pude registrarte. Verifica que el backend esté corriendo.');
          this.startLoading.set(false);
        }
      });
  }

  enviar(): void {
    const texto = this.draft().trim();
    const estudiante = this.student();
    if (!texto || this.loading() || !estudiante) {
      return;
    }

    this.messages.update((msgs) => [...msgs, { role: 'student', text: texto }]);
    this.draft.set('');
    this.loading.set(true);

    this.http
      .post<ChatResponse>(`${environment.apiUrl}/api/chat`, {
        student_id: estudiante.id,
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

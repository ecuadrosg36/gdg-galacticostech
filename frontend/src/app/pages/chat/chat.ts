import { Component, signal } from '@angular/core';
import { FormsModule } from '@angular/forms';

import { StudentService } from '../../../services/student.service';
import { TutorService } from '../../../services/tutor.service';
import { StudentLoginResponse } from '../../../models/api.models';

interface ChatMessage {
  role: 'student' | 'gemma';
  text: string;
}

@Component({
  selector: 'app-chat',
  standalone: true,
  imports: [FormsModule],
  templateUrl: './chat.html',
  styleUrl: './chat.css'
})
export class Chat {
  protected readonly grados = [
    'Primero de primaria',
    'Segundo de primaria',
    'Tercero de primaria'
  ];

  // Identificación del estudiante (no es login/autenticación: sin contraseña,
  // solo nombre + grado, apropiado para niños de primaria). Internamente
  // llama a POST /api/students/login, que busca por nombre+grado antes de
  // crear uno nuevo (evita duplicar estudiantes en cada prueba) y abre una
  // ChatSession real en la base de datos.
  protected readonly student = signal<StudentLoginResponse | null>(null);
  protected readonly nombreInput = signal('');
  protected readonly gradoInput = signal(this.grados[0]);
  protected readonly startError = signal<string | null>(null);
  protected readonly startLoading = signal(false);

  protected readonly messages = signal<ChatMessage[]>([]);
  protected readonly draft = signal('');
  protected readonly loading = signal(false);
  protected readonly mode = signal<string | null>(null);

  constructor(
    private readonly studentService: StudentService,
    private readonly tutorService: TutorService
  ) {}

  comenzar(): void {
    const nombre = this.nombreInput().trim();
    if (!nombre || this.startLoading()) {
      return;
    }

    this.startLoading.set(true);
    this.startError.set(null);

    this.studentService
      .login({ nombre, grado: this.gradoInput() })
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

    this.tutorService
      .sendMessage({
        student_id: estudiante.id,
        session_id: estudiante.chat_session_id,
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

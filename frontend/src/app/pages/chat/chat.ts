import { Component, OnDestroy, computed, input, signal } from '@angular/core';
import { FormsModule } from '@angular/forms';

import { StudentService } from '../../../services/student.service';
import { TutorService } from '../../../services/tutor.service';
import { StudentLoginResponse } from '../../../models/api.models';

interface ChatMessage {
  role: 'student' | 'gemma';
  text: string;
}

const MATERIA_LABELS: Record<string, string> = {
  matematica: 'matemática',
  comunicacion: 'comunicación',
  personal_social: 'personal social'
};

@Component({
  selector: 'app-chat',
  standalone: true,
  imports: [FormsModule],
  templateUrl: './chat.html',
  styleUrl: './chat.css'
})
export class Chat implements OnDestroy {
  // Viene de /chat?materia=... (ver /materias y la sección de Inicio, que
  // enlazan aquí con [queryParams]). withComponentInputBinding() en
  // app.config.ts hace que Angular lo ligue automáticamente a este input.
  readonly materia = input<string>('matematica');
  protected readonly materiaLabel = computed(() => MATERIA_LABELS[this.materia()] ?? 'tus materias');

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

  // Preguntar por voz (Web Speech API): transcribe en el navegador y llena
  // el campo de texto, no reemplaza el backend/tutor. Requiere internet
  // para el reconocimiento de voz (servicio del navegador); las respuestas
  // de Gemma siguen siendo 100% locales/offline.
  protected readonly listening = signal(false);
  protected readonly voiceSupported = signal(false);
  private recognition: any = null;

  // Leer la respuesta en voz alta (Web Speech API - SpeechSynthesis). A
  // diferencia del micrófono, esto corre 100% en el navegador/SO, sin
  // internet. Es opt-in: nunca se reproduce sola, solo si el estudiante
  // toca el botón 🔊 de esa respuesta puntual.
  protected readonly ttsSupported = signal(false);
  protected readonly speakingIndex = signal<number | null>(null);
  private synth: SpeechSynthesis | null = null;

  constructor(
    private readonly studentService: StudentService,
    private readonly tutorService: TutorService
  ) {
    const SpeechRecognitionCtor =
      typeof window !== 'undefined' && ((window as any).SpeechRecognition || (window as any).webkitSpeechRecognition);

    if (SpeechRecognitionCtor) {
      this.voiceSupported.set(true);
      this.recognition = new SpeechRecognitionCtor();
      this.recognition.lang = 'es-PE';
      this.recognition.continuous = false;
      this.recognition.interimResults = true;

      this.recognition.onresult = (event: any) => {
        let transcript = '';
        for (let i = event.resultIndex; i < event.results.length; i++) {
          transcript += event.results[i][0].transcript;
        }
        this.draft.set(transcript);
      };

      this.recognition.onend = () => {
        this.listening.set(false);
        if (this.draft().trim()) {
          this.enviar();
        }
      };

      this.recognition.onerror = () => {
        this.listening.set(false);
      };
    }

    if (typeof window !== 'undefined' && 'speechSynthesis' in window) {
      this.ttsSupported.set(true);
      this.synth = window.speechSynthesis;
    }
  }

  ngOnDestroy(): void {
    this.synth?.cancel();
  }

  protected leerEnVozAlta(texto: string, index: number): void {
    if (!this.synth) {
      return;
    }

    // Tocar el mismo botón mientras habla = detener.
    if (this.speakingIndex() === index) {
      this.synth.cancel();
      this.speakingIndex.set(null);
      return;
    }

    this.synth.cancel();
    const utterance = new SpeechSynthesisUtterance(this.textoPlano(texto));
    utterance.lang = 'es-PE';
    utterance.rate = 0.95;
    utterance.onend = () => this.speakingIndex.set(null);
    utterance.onerror = () => this.speakingIndex.set(null);

    this.speakingIndex.set(index);
    this.synth.speak(utterance);
  }

  // Igual que formatearTexto(), pero sin etiquetas HTML: para que el
  // lector de voz no lea literalmente los símbolos de Markdown si Gemma
  // llegara a devolver alguno.
  private textoPlano(texto: string): string {
    return texto
      .replace(/\$\$(.+?)\$\$/g, '$1')
      .replace(/\$(.+?)\$/g, '$1')
      .replace(/\*\*(.+?)\*\*/g, '$1')
      .replace(/^#{1,6}\s*/gm, '')
      .replace(/^[-*]\s+/gm, '');
  }

  // Red de seguridad: el prompt le pide a Gemma texto plano, pero a veces
  // igual devuelve Markdown/LaTeX (**negrita**, $$formula$$). Como no hay
  // un renderer de Markdown en el chat, sin esto se veían los símbolos
  // literales en pantalla. Escapa HTML primero (por seguridad, ya que el
  // texto viene de un LLM) y recién ahí interpreta **negrita**.
  protected formatearTexto(texto: string): string {
    const escapado = texto
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;');

    return escapado
      .replace(/\$\$(.+?)\$\$/g, '$1')
      .replace(/\$(.+?)\$/g, '$1')
      .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
      .replace(/^#{1,6}\s*/gm, '')
      .replace(/^[-*]\s+/gm, '• ');
  }

  toggleMic(): void {
    if (!this.recognition || this.loading()) {
      return;
    }

    if (this.listening()) {
      this.recognition.stop();
      this.listening.set(false);
      return;
    }

    this.draft.set('');
    this.listening.set(true);
    this.recognition.start();
  }

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
            { role: 'gemma', text: `Hola, ${res.nombre.split(' ')[0]}. Soy Gemma. Pregúntame lo que quieras sobre ${this.materiaLabel()}.` }
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
        message: texto,
        materia: this.materia()
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

import { Component, OnInit, signal } from '@angular/core';
import { HttpClient } from '@angular/common/http';

import { environment } from '../../../environments/environment';

interface Student {
  id: number;
  nombre: string;
  grado: string;
  localidad: string | null;
}

@Component({
  selector: 'app-profesor',
  standalone: true,
  template: `
    <header class="head">
      <div>
        <h2>Panel del Docente</h2>
        <p>Currículo MINEDU · Datos reales de esta sesión</p>
      </div>
    </header>

    <section class="stats">
      <div class="stat-card">
        <span class="icon">👥</span>
        <p class="label">Total Estudiantes</p>
        <h3>{{ students().length }}</h3>
      </div>
      <div class="stat-card muted">
        <span class="icon">📘</span>
        <p class="label">Materiales</p>
        <h3>Próximamente</h3>
      </div>
      <div class="stat-card muted">
        <span class="icon">📝</span>
        <p class="label">Evaluaciones</p>
        <h3>Próximamente</h3>
      </div>
      <div class="stat-card muted">
        <span class="icon">📈</span>
        <p class="label">Progreso</p>
        <h3>Próximamente</h3>
      </div>
    </section>

    <section class="students-section">
      <h3>Estudiantes registrados</h3>
      @if (error()) {
        <p class="error">No pude cargar la lista. Verifica que el backend esté corriendo.</p>
      }
      <div class="student-list">
        @for (s of students(); track s.id) {
          <div class="student-row">
            <div class="avatar">{{ s.nombre.charAt(0) }}</div>
            <div class="info">
              <h4>{{ s.nombre }}</h4>
              <p>
                {{ s.grado }}
                @if (s.localidad) {
                  · {{ s.localidad }}
                }
              </p>
            </div>
          </div>
        }
      </div>
    </section>

    <section class="actions">
      <h3>Acciones rápidas</h3>
      <div class="action-grid">
        <button class="action muted" disabled>
          <span>📤</span>
          Subir Material
          <small>Próximamente</small>
        </button>
        <button class="action muted" disabled>
          <span>✅</span>
          Crear Evaluación
          <small>Próximamente</small>
        </button>
        <button class="action muted" disabled>
          <span>📊</span>
          Ver Reportes
          <small>Próximamente</small>
        </button>
      </div>
    </section>
  `,
  styleUrl: './profesor.css'
})
export class Profesor implements OnInit {
  protected readonly students = signal<Student[]>([]);
  protected readonly error = signal(false);

  constructor(private readonly http: HttpClient) {}

  ngOnInit(): void {
    this.http.get<Student[]>(`${environment.apiUrl}/api/students`).subscribe({
      next: (res) => this.students.set(res),
      error: () => this.error.set(true)
    });
  }
}

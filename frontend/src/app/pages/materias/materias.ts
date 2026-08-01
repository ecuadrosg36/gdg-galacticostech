import { Component } from '@angular/core';
import { RouterLink } from '@angular/router';

@Component({
  selector: 'app-materias',
  standalone: true,
  imports: [RouterLink],
  template: `
    <div class="badge">⭐ ¡Hola, explorador!</div>
    <h2>📚 ¿Qué quieres aprender hoy?</h2>
    <p class="subtitle">Elige una materia para comenzar.</p>

    <a routerLink="/chat" class="subject-row math">
      <div class="icon">🧮</div>
      <div class="text">
        <h3>Matemática</h3>
        <p>Números, operaciones y problemas.</p>
      </div>
      <span class="arrow">›</span>
    </a>

    <a routerLink="/chat" class="subject-row comm">
      <div class="icon">📖</div>
      <div class="text">
        <h3>Comunicación</h3>
        <p>Lectura, escritura y comprensión.</p>
      </div>
      <span class="arrow">›</span>
    </a>

    <a routerLink="/chat" class="subject-row social">
      <div class="icon">🌎</div>
      <div class="text">
        <h3>Personal Social</h3>
        <p>Historia, ciudadanía y cultura del Perú.</p>
      </div>
      <span class="arrow">›</span>
    </a>
  `,
  styleUrl: './materias.css'
})
export class Materias {}

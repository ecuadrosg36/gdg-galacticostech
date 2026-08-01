import { Component } from '@angular/core';
import { RouterLink } from '@angular/router';

@Component({
  selector: 'app-home',
  standalone: true,
  imports: [RouterLink],
  template: `
    <section class="welcome">
      <div class="mascot"><img src="/img/gemma-mascot.png" alt="Gemma" /></div>
      <div>
        <p class="hi">¡Hola!</p>
        <h2>Soy Gemma 😊<br /><span>Seré tu compañera de aprendizaje.</span></h2>
      </div>
    </section>

    <section class="hero">
      <img src="/img/hero-illustration.png" alt="Estudiantes aprendiendo con Galácticos Tech" />
    </section>

    <section class="section">
      <div class="section-head">
        <h3>📚 ¿Qué quieres aprender hoy?</h3>
        <a routerLink="/materias">Ver todo ›</a>
      </div>
      <div class="subject-grid">
        <a routerLink="/chat" [queryParams]="{ materia: 'matematica' }" class="subject-card">
          <span class="icon">📘</span>
          <div>
            <h4>Matemática</h4>
            <p>Sumas, restas y problemas</p>
          </div>
        </a>
        <a routerLink="/chat" [queryParams]="{ materia: 'comunicacion' }" class="subject-card">
          <span class="icon">📖</span>
          <div>
            <h4>Comunicación</h4>
            <p>Lectura y comprensión</p>
          </div>
        </a>
        <a routerLink="/chat" [queryParams]="{ materia: 'personal_social' }" class="subject-card wide">
          <span class="icon">🌎</span>
          <div>
            <h4>Personal Social</h4>
            <p>Historia y ciudadanía</p>
          </div>
        </a>
      </div>
    </section>

    <section class="official-strip">
      <span class="icon">🎓</span>
      <div>
        <h4>Contenido oficial</h4>
        <p>Currículo oficial de MINEDU / Perú Educa.</p>
      </div>
    </section>

    <a routerLink="/chat" class="cta">
      <span class="cta-icon"><img src="/img/gemma-mascot.png" alt="" /></span>
      <div>
        <h4>Habla con Gemma</h4>
        <p>Resuelve tus dudas en cualquier momento.</p>
      </div>
      <span class="chevron">›</span>
    </a>

    <a routerLink="/profesor" class="teacher-link">👩‍🏫 Panel del docente</a>
  `,
  styleUrl: './home.css'
})
export class Home {}

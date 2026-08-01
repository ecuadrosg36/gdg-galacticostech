import { Component, Input } from '@angular/core';

@Component({
  selector: 'app-placeholder',
  standalone: true,
  template: `
    <div class="wrap">
      <div class="icon">🚧</div>
      <h2>{{ titulo }}</h2>
      <p>Estamos construyendo esta sección. ¡Vuelve pronto!</p>
    </div>
  `,
  styles: [`
    :host { display: block; height: 100%; }
    .wrap {
      height: 100%;
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      text-align: center;
      gap: 8px;
      padding: 40px 24px;
      color: var(--on-surface-variant, #434656);
    }
    .icon { font-size: 2.5rem; }
    h2 { margin: 0; color: var(--on-surface, #0b1c30); font-size: 1.2rem; }
    p { margin: 0; font-size: 0.9rem; }
  `]
})
export class Placeholder {
  @Input() titulo = 'Próximamente';
}

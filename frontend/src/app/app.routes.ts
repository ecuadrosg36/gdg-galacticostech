import { Routes } from '@angular/router';
import { Home } from './pages/home/home';
import { Materias } from './pages/materias/materias';
import { Chat } from './pages/chat/chat';
import { Placeholder } from './pages/placeholder/placeholder';
import { Profesor } from './pages/profesor/profesor';

export const routes: Routes = [
  { path: '', component: Home },
  { path: 'materias', component: Materias },
  { path: 'chat', component: Chat },
  { path: 'profesor', component: Profesor },
  { path: 'progreso', component: Placeholder, data: { titulo: 'Progreso' } },
  { path: 'ayuda', component: Placeholder, data: { titulo: 'Ayuda' } },
  { path: '**', redirectTo: '' }
];

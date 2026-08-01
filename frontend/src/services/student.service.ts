// src/app/services/student.service.ts

import { Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../environments/environment';
import { 
  Student, 
  StudentCreate, 
  StudentUpdate, 
  StudentLoginResponse 
} from '../models/api.models';

@Injectable({
  providedIn: 'root'
})
export class StudentService {
  // Asumimos que tus endpoints de estudiante tienen el prefijo /api/students
  private apiUrl = `${environment.apiUrl}/api/students`;

  constructor(private http: HttpClient) {}

  /**
   * LOGIN: Ingresa o registra un estudiante y crea su sesión de chat
   * POST /api/students/login
   */
  login(data: StudentCreate): Observable<StudentLoginResponse> {
    return this.http.post<StudentLoginResponse>(`${this.apiUrl}/login`, data);
  }

  /**
   * LISTAR: Obtiene todos los estudiantes, con filtros opcionales
   * GET /api/students?grado=X&localidad=Y
   */
  getStudents(grado?: string, localidad?: string): Observable<Student[]> {
    // HttpParams nos ayuda a construir la URL con los filtros de forma segura
    let params = new HttpParams();
    
    if (grado) {
      params = params.set('grado', grado);
    }
    if (localidad) {
      params = params.set('localidad', localidad);
    }

    return this.http.get<Student[]>(this.apiUrl, { params });
  }

  /**
   * OBTENER UNO: Busca un estudiante por su ID
   * GET /api/students/{id}
   */
  getStudent(id: number): Observable<Student> {
    return this.http.get<Student>(`${this.apiUrl}/${id}`);
  }

  /**
   * CREAR: Crea un estudiante directamente (sin crear sesión de chat)
   * Útil para el panel de administración del profesor
   * POST /api/students
   */
  createStudent(data: StudentCreate): Observable<Student> {
    return this.http.post<Student>(this.apiUrl, data);
  }

  /**
   * ACTUALIZAR: Modifica los datos de un estudiante
   * PUT /api/students/{id}
   */
  updateStudent(id: number, data: StudentUpdate): Observable<Student> {
    return this.http.put<Student>(`${this.apiUrl}/${id}`, data);
  }

  /**
   * ELIMINAR: Borra un estudiante
   * DELETE /api/students/{id}
   */
  deleteStudent(id: number): Observable<void> {
    return this.http.delete<void>(`${this.apiUrl}/${id}`);
  }
}
import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../environments/environment';

export interface Model {
  id: string;
  name: string;
  description?: string;
}

@Injectable({ providedIn: 'root' })
export class ModelService {
  private apiUrl = `${environment.apiUrl}/models`;

  constructor(private http: HttpClient) {}

  getAvailableModels(): Observable<Model[]> {
    return this.http.get<Model[]>(`${this.apiUrl}/`);
  }
}

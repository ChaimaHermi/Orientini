import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../environments/environment';

@Injectable({
  providedIn: 'root'
})
export class UserService {
  private apiUrl = `${environment.apiUrl}/users`;

  constructor(
    private http: HttpClient  ) {}

  getCurrentUser(): Observable<any> {
    return this.http.get<any>(`${this.apiUrl}/me`);
  }

  
  getUserId(): Observable<any> {
    return this.http.get(`${this.apiUrl}/me`);
  }

  getUserEmail(): Observable<any> {
    return this.http.get(`${this.apiUrl}/email`);
  }

  getAllUsers(): Observable<any[]> {
    return this.http.get<any[]>(this.apiUrl);
  }

  updateUserEmail(userId: string, newEmail: string): Observable<any> {
    return this.http.put(`${this.apiUrl}/${userId}`, { email: newEmail});
  }

  deleteUser(userId: string): Observable<any> {
    return this.http.delete(`${this.apiUrl}/${userId}`);
  }
}

import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Observable, catchError, throwError } from 'rxjs';
import { environment } from '../environments/environment';
import { SharedService } from './shared.service';

@Injectable({
  providedIn: 'root'
})
export class ChatService {
  private apiUrl = `${environment.apiUrl}/chat`;

  constructor(
    private http: HttpClient,
    private sharedService: SharedService
  ) {}

  private getHeaders(): HttpHeaders {
    const token = this.sharedService.getToken();
    return new HttpHeaders({
      Authorization: `Bearer ${token}`
    });
  }
sendQuestion(question: string, conversationId?: string) {
  const formData = new FormData();
  formData.append('question', question);

  if (conversationId && conversationId !== 'default') {
    formData.append('conversation_id', conversationId);
  }

  return this.http.post<any>(
    `${this.apiUrl}/ask`,
    formData,
    { headers: this.getHeaders() }
  );
}

  getConversations(): Observable<any> {
    return this.http.get<any>(`${this.apiUrl}/conversations`, {
      headers: this.getHeaders()
    });
  }

  getConversationMessages(conversationId: string): Observable<any> {
    return this.http.get<any>(`${this.apiUrl}/conversations/${conversationId}`, {
      headers: this.getHeaders()
    }).pipe(
      catchError((error) => {
        console.error('[ERREUR] Récupération des messages:', error);
        return throwError(() => error);
      })
    );
  }

  deleteConversation(conversationId: string): Observable<any> {
  return this.http.delete<any>(
    `${this.apiUrl}/conversations/${conversationId}`,
    {       headers: this.getHeaders()
 }
  );
}

}

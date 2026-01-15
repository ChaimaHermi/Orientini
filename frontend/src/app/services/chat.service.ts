import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../environments/environment';
import { ChatResponse } from '../models/chat-response.model';
import { Conversation } from '../models/conversation.model';
import { Message } from '../models/message.model';

@Injectable({
  providedIn: 'root'
})
export class ChatService {

  private apiUrl = `${environment.apiUrl}/chat`;

  constructor(private http: HttpClient) {}

  // ✅ ICI on retourne ChatResponse (PAS Message)
  sendQuestion(
    question: string,
    conversationId?: string
  ): Observable<ChatResponse> {

    const formData = new FormData();
    formData.append('question', question);

    if (conversationId) {
      formData.append('conversation_id', conversationId);
    }

    return this.http.post<ChatResponse>(
      `${this.apiUrl}/ask`,
      formData
    );
  }

  getConversations(): Observable<Conversation[]> {
    return this.http.get<Conversation[]>(
      `${this.apiUrl}/conversations`
    );
  }

  getConversationMessages(conversationId: string): Observable<Message[]> {
    return this.http.get<Message[]>(
      `${this.apiUrl}/conversations/${conversationId}`
    );
  }

  deleteConversation(conversationId: string): Observable<void> {
    return this.http.delete<void>(
      `${this.apiUrl}/conversations/${conversationId}`
    );
  }
}

import { CommonModule } from '@angular/common';
import { Component, OnInit } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { ActivatedRoute, Router } from '@angular/router';

import { ChatInputComponent } from '../../components/chat-input/chat-input.component';
import { SidebarComponent } from '../../components/sidebar/sidebar.component';
import { ChatMessagesComponent } from '../../components/chat-messages/chat-messages.component';

import { ChatService } from '../../../../services/chat.service';
import { UserService } from '../../../../services/user.service';
import { Message } from '../../../../models/message.model';

interface Conversation {
  id: string;
  title: string;
  date: Date;
}

@Component({
  selector: 'app-chat-page',
  standalone: true,
  imports: [
    CommonModule,
    FormsModule,
    ChatInputComponent,
    SidebarComponent,
    ChatMessagesComponent
  ],
  templateUrl: './chat-page.component.html',
  styleUrls: ['./chat-page.component.scss']
})
export class ChatPageComponent implements OnInit {

  sidebarOpen = true;
  isLoading = false;

  userId = '';
  conversations: Conversation[] = [];
  currentMessages: Message[] = [];
  currentConversationId: string = 'default';

  constructor(
    private chatService: ChatService,
    private userService: UserService,
    private route: ActivatedRoute,
    private router: Router
  ) {}

  /* =======================
     INIT
  ======================= */
  ngOnInit(): void {
    this.userService.getUserId().subscribe({
      next: (res) => {
        this.userId = res.user_id;

        this.chatService.getConversations().subscribe({
          next: (convs) => {
            this.conversations = convs.map((c: any) => ({
              id: c.id,
              title: c.title,
              date: new Date(c.created_at)
            }));

            const routeId = this.route.snapshot.paramMap.get('id');
            if (routeId && routeId !== 'default') {
              const conv = this.conversations.find(c => c.id === routeId);
              if (conv) {
                this.onSelectConversation(conv);
              }
            }
          }
        });
      }
    });
  }

  /* =======================
     UI
  ======================= */
  toggleSidebar() {
    this.sidebarOpen = !this.sidebarOpen;
  }

  onNewChat() {
    this.currentMessages = [];
    this.currentConversationId = 'default';
    this.router.navigate(['/c', 'default']);
  }

  /* =======================
     SEND MESSAGE
  ======================= */
  onSendMessage(message: string) {
    if (!message.trim()) return;

    // Message utilisateur
    this.currentMessages.push({
      id: crypto.randomUUID(),
      content: message,
      isUser: true,
      timestamp: new Date()
    });

    this.isLoading = true;

    this.chatService.sendQuestion(message, this.currentConversationId)
      .subscribe({
        next: (response) => {

          console.log('📩 Réponse API complète :', response);

          // MAJ conversation
          if (this.currentConversationId === 'default') {
            this.currentConversationId = response.conversation_id;
            this.router.navigate(['/c', response.conversation_id]);

            this.conversations.unshift({
              id: response.conversation_id,
              title: response.conversation_title,
              date: new Date()
            });
          }

          // 🔥 MESSAGE ASSISTANT AVEC IMAGES
          this.currentMessages.push({
            id: crypto.randomUUID(),
            content: response.answer,
            images: response.images,   // ✅ OBLIGATOIRE
            isUser: false,
            timestamp: new Date()
          });

          this.isLoading = false;
        },
        error: () => {
          this.isLoading = false;
        }
      });
  }

  /* =======================
     LOAD CONVERSATION
  ======================= */
  onSelectConversation(conversation: Conversation) {
    this.currentConversationId = conversation.id;
    this.currentMessages = [];
    this.isLoading = true;

    this.router.navigate(['/c', conversation.id]);

    this.chatService.getConversationMessages(conversation.id)
      .subscribe({
        next: (messages) => {

          console.log('📜 Messages chargés :', messages);

          this.currentMessages = messages.map((msg: any) => ({
            id: crypto.randomUUID(),
            content: msg.content,
            images: msg.images,       // ✅ IMPORTANT
            isUser: msg.role === 'user',
            timestamp: new Date(msg.created_at)
          }));

          this.isLoading = false;
        },
        error: () => {
          this.isLoading = false;
        }
      });
  }
}

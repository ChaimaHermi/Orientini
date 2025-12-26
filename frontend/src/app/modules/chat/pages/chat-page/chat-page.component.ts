import { CommonModule } from '@angular/common';
import { Component } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { ChatInputComponent } from '../../components/chat-input/chat-input.component';
import { SidebarComponent } from '../../components/sidebar/sidebar.component';
import { ChatMessagesComponent } from '../../components/chat-messages/chat-messages.component';
import { ChatService } from '../../../../services/chat.service';
import { Message } from '../../../../models/message.model';
import { UserService } from '../../../../services/user.service';
import { ActivatedRoute, Router } from '@angular/router';

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
export class ChatPageComponent {

  isSidebarOpen = true;
  isLoading = false;

  currentMessages: Message[] = [];

  sidebarOpen = true;
  uploadedFiles: File[] = [];
  userId: string = '';
  conversations: Conversation[] = [];
currentConversationId: string = 'default';

  constructor(
    private chatService: ChatService,
    private userService: UserService,
    private route: ActivatedRoute,
    private router: Router
  ) {}

  ngOnInit(): void {

    console.log('[INIT] Récupération de l\'ID utilisateur...');
    this.userService.getUserId().subscribe({
      next: (res) => {
        this.userId = res.user_id;
        console.log('[INIT] userId récupéré :', this.userId);

        console.log('[INIT] Chargement des conversations...');
        this.chatService.getConversations().subscribe({
          next: (convs) => {
            this.conversations = convs.map((c: any) => ({
              id: c.id,
              title: c.title,
              date: c.created_at ? new Date(c.created_at) : new Date()
            }));
            console.log('[INIT] Conversations chargées :', this.conversations);

            const routeId = this.route.snapshot.paramMap.get('id');
            console.log('[INIT] ID de route détecté :', routeId);

            if (routeId && routeId !== 'default') {
              const conv = this.conversations.find(c => c.id === routeId);
              if (conv) {
                console.log('[INIT] Reprise de conversation via URL :', routeId);
                this.onSelectConversation(conv);
              }
               else {
    this.router.navigate(['/c', 'default']);
  }
            } else {
              console.log('[INIT] Aucune conversation sélectionnée → redirection vers /c/default');
              this.router.navigate(['/c', 'default']);
            }
          }
        });
      }
    });
  }

  toggleSidebar() {
    this.sidebarOpen = !this.sidebarOpen;
  }

onSendMessage(message: string) {
  if (!message.trim()) return;

  this.isLoading = true;

  // afficher le message utilisateur immédiatement
  this.currentMessages.push({
    id: Date.now().toString(),
    content: message,
    isUser: true,
    timestamp: new Date()
  });

  this.chatService.sendQuestion(message, this.currentConversationId)
    .subscribe({
      next: (response) => {
        const conversationId = response.conversation_id;
        const conversationTitle = response.conversation_title;

        // 🆕 ajouter à la sidebar si nouvelle
        if (!this.conversations.find(c => c.id === conversationId)) {
          this.conversations.unshift({
            id: conversationId,
            title: conversationTitle,
            date: new Date()
          });
        }

        // redirection si default
        if (this.currentConversationId === 'default') {
          this.currentConversationId = conversationId;
          this.router.navigate(['/c', conversationId]);
        }

        // afficher réponse IA
        this.currentMessages.push({
          id: Date.now().toString(),
          content: response.answer,
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


onSelectConversation(conversation: Conversation) {
  this.currentConversationId = conversation.id;
  this.currentMessages = [];
  this.isLoading = true;

  this.router.navigate(['/c', conversation.id]);

  this.chatService.getConversationMessages(conversation.id)
    .subscribe({
      next: (messages) => {
        this.currentMessages = messages.map((msg: any, i: number) => ({
          id: i.toString(),
          content: msg.content,
          isUser: msg.role === 'user', // ✅ CORRIGÉ
          timestamp: new Date(msg.created_at)
        }));
        this.isLoading = false;
      },
      error: () => {
        this.isLoading = false;
      }
    });
}


  onNewChat() {
    console.log('[NEW CHAT] 🔄 Réinitialisation du fil de messages');
    this.currentMessages = [];
    this.currentConversationId = 'default';

    console.log('[NEW CHAT] Redirection vers /c/default');
    this.router.navigate(['/c', 'default']);
  }
}

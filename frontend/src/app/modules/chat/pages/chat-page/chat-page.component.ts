import { CommonModule } from '@angular/common';
import { Component } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { ChatInputComponent } from '../../components/chat-input/chat-input.component';
import { SidebarComponent } from '../../components/sidebar/sidebar.component';
import { ModelSelectorComponent } from '../../components/model-selector/model-selector.component';
import { ChatMessagesComponent } from '../../components/chat-messages/chat-messages.component';
import { FileUploaderComponent } from '../../components/file-uploader/file-uploader.component';
import { FileViewerComponent } from '../../components/file-viewer/file-viewer.component';
import { ChatService } from '../../../../services/chat.service';
import { Message } from '../../../../models/message.model';
import { UserService } from '../../../../services/user.service';
import { ModelService } from '../../../../services/model.service';
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
    ModelSelectorComponent,
    ChatMessagesComponent,
    FileUploaderComponent,
    FileViewerComponent
  ],
  templateUrl: './chat-page.component.html',
  styleUrls: ['./chat-page.component.scss']
})
export class ChatPageComponent {
  showFileUploader = false;
  viewedFile: any = null;
  isSidebarOpen = true;
  isLoading = false;

  availableModels: any[] = [];
  currentModel: any = null;

  currentMessages: Message[] = [];

  sidebarOpen = true;
  uploadedFiles: File[] = [];
  userId: string = '';
  conversations: Conversation[] = [];
currentConversationId: string = 'default';

  constructor(
    private chatService: ChatService,
    private userService: UserService,
    private modelService: ModelService,
    private route: ActivatedRoute,
    private router: Router
  ) {}

  ngOnInit(): void {
    console.log('[INIT] Chargement des modèles disponibles...');
    this.modelService.getAvailableModels().subscribe({
      next: (models) => {
        this.availableModels = models;
        this.currentModel = models[0];
        console.log('[INIT] Modèle courant :', this.currentModel);
      }
    });

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
              date: new Date(c.date)
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
    console.log('[SEND] Message envoyé :', message);
  if (!message.trim() || !this.userId) return;

  this.isLoading = true;
  const file = this.uploadedFiles.length > 0 ? this.uploadedFiles[0] : null;
  const model = this.currentModel?.id;
  const currentRouteId = this.route.snapshot.paramMap.get('id');

  // 1. Ajouter immédiatement le message utilisateur dans le fil
  this.currentMessages.push({
    id: Date.now().toString(),
    content: message,
    isUser: true,
    timestamp: new Date(),
    files: file ? [file] : []
  });

  this.chatService.sendQuestion(message, file, model, this.currentConversationId).subscribe({
    next: (response) => {
      const conversationId = response.metadata?.conversation_id;
      const conversationName = response.metadata?.conversation_name;
      const chunksUsed = response.metadata?.chunks_used || [];
      if (chunksUsed.length > 0) {
        console.log('[CHUNKS] Chunks utilisés pour la réponse :');
        chunksUsed.forEach((chunk: any, index: number) => {
          console.log(`Chunk ${index + 1} - Page: ${chunk.metadata?.page}, Score: ${chunk.score}`);
          console.log('Contenu:', chunk.content.slice(0, 200)); // Affiche les 200 premiers caractères
        });
      }

      // 2. Ajouter la conversation à la sidebar si elle est nouvelle
      const alreadyExists = this.conversations.find(c => c.id === conversationId);
      if (!alreadyExists) {
        const newConv = {
          id: conversationId,
          title: conversationName,
          date: new Date()
        };
        this.conversations.unshift(newConv);
        console.log('[SIDEBAR] Nouvelle conversation ajoutée :', newConv);
      }

      // 3. Rediriger vers /c/:id si on est encore dans /c/default
      if (currentRouteId === 'default') {
        console.log('[ROUTER] Redirection vers /c/' + conversationId);
        this.currentConversationId = conversationId;
        this.router.navigate(['/c', conversationId]).then(() => {
          // 4. Recharger automatiquement les messages de la conversation
          this.onSelectConversation({
            id: conversationId,
            title: conversationName,
            date: new Date()
          });
        });
      }
       else {
        this.currentConversationId = conversationId;
      }

      // 5. Afficher la réponse dans le fil de discussion
      this.currentMessages.push({
        id: Date.now().toString(),
        content: response.answer,
        isUser: false,
        timestamp: new Date(),
        model_used: response.metadata.model_used 
      });

      this.uploadedFiles = [];
      this.isLoading = false;
    },

    error: (error) => {
      this.currentMessages.push({
        id: Date.now().toString(),
        content: 'Erreur IA : ' + (error.error?.error || 'Erreur inconnue'),
        isUser: false,
        timestamp: new Date(),
        files: []
      });
      this.isLoading = false;
      }
    });
  }

onSelectConversation(conversation: Conversation) {
  console.log('[SELECT] Conversation sélectionnée :', conversation);

  this.router.navigate(['/c', conversation.id]);
  this.currentMessages = [];
  this.isLoading = true;
  this.currentConversationId = conversation.id;

  this.chatService.getConversationMessages(conversation.id).subscribe({
    next: (res) => {
      console.log('[SELECT] Messages chargés pour la conversation :', res);

      this.currentMessages = res.messages.map((msg: any, index: number) => ({
        id: index.toString(),
        content: msg.content,
        isUser: msg.role === 'user',
        timestamp: new Date(msg.created_at),
        files: msg.files || [],
        model: msg.model_name
      }));

      this.isLoading = false;
    },
    error: (err) => {
      console.error('[SELECT] ❌ Erreur lors du chargement des messages :', err);
      this.currentMessages = [{
        id: 'error',
        content: 'Erreur lors du chargement de la conversation.',
        isUser: false,
        timestamp: new Date(),
        files: []
      }];
      this.isLoading = false;
    }
  });
}

  onFileUpload(files: File[]) {
    this.uploadedFiles = files;
    this.showFileUploader = false;
  }

  onRemoveFile(file: File) {
    this.uploadedFiles = this.uploadedFiles.filter(f => f !== file);
  }

  onViewFile(file: File) {
    this.viewedFile = file;
  }

  onModelChange(model: any) {
    this.currentModel = model;
  }

  onNewChat() {
    console.log('[NEW CHAT] 🔄 Réinitialisation du fil de messages');
    this.currentMessages = [];
    this.uploadedFiles = [];
    this.currentConversationId = 'default';

    console.log('[NEW CHAT] Redirection vers /c/default');
    this.router.navigate(['/c', 'default']);
  }
}

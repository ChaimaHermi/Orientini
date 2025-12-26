import { CommonModule } from '@angular/common';
import { Component, EventEmitter, Input, Output } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { Router } from '@angular/router';
import { SharedService } from '../../../../services/shared.service';
import { ChatService } from '../../../../services/chat.service';
import { AuthService } from '../../../../services/auth.service';
import { UserService } from '../../../../services/user.service';

interface Conversation {
  id: string;
  title: string;
  date: Date;
}

@Component({
  selector: 'app-sidebar',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './sidebar.component.html',
  styleUrls: ['./sidebar.component.scss']
})
export class SidebarComponent {
  @Input() sidebarOpen = true;
  @Input() conversations: Conversation[] = [];
  @Output() newChat = new EventEmitter<void>();
  @Output() selectConversation = new EventEmitter<Conversation>();
  @Output() sidebarToggled = new EventEmitter<void>();

  userEmail: string = '';
  activeConversationId: string = '';
  userProfilePicture: string = '';
  defaultProfilePicture: string = '/assets/img/default-user.png';
  constructor(
    private sharedService: SharedService,
    private authService: AuthService,
    private userService: UserService,
    private chatService: ChatService,
    private router: Router
  ) {}


ngOnInit(): void {
  this.userService.getCurrentUser().subscribe({
    next: (res) => {
      const googleImage = res.profile_picture || '';
const proxiedImage = googleImage
  ? `https://images.weserv.nl/?url=${encodeURIComponent(googleImage)}`
  : '/assets/img/default-user.png';

      console.log("Image à afficher :", proxiedImage);

      this.userEmail = res.email;
      this.userProfilePicture = proxiedImage;
    },
    error: (err) => {
      console.error('Erreur récupération profil :', err);
    }
  });
}


onImageError(): void {
  this.userProfilePicture = this.defaultProfilePicture;
}
onSelect(conversation: Conversation): void {
  this.activeConversationId = conversation.id;
  this.selectConversation.emit(conversation);
}

isActive(conversation: Conversation): boolean {
  return conversation.id === this.activeConversationId;
}

  onToggleSidebar(): void {
    this.sidebarOpen = !this.sidebarOpen;
    this.sidebarToggled.emit();
  }

  logout(): void {
    this.sharedService.clearAuthInfo();
    this.router.navigate(['/auth/login']);
  }

  onNewChatClick(): void {
  this.activeConversationId = ''; // Réinitialise l'élément actif visuellement
  this.newChat.emit();            // Informe le parent
}

onDeleteConversation(conversationId: string, event: Event) {
  event.stopPropagation();

  if (!confirm('Supprimer cette conversation ?')) return;

  this.chatService.deleteConversation(conversationId).subscribe({
    next: () => {
      this.conversations = this.conversations.filter(c => c.id !== conversationId);
      if (this.activeConversationId === conversationId) {
        this.activeConversationId = '';
        this.newChat.emit();
      }
    }
  });
}



}
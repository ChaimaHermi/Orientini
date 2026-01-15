import { CommonModule } from '@angular/common';
import { Component, Input } from '@angular/core';
import { DomSanitizer, SafeHtml } from '@angular/platform-browser';
import { Message } from '../../../../models/message.model';
import { environment } from '../../../../environments/environment';

@Component({
  selector: 'app-chat-messages',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './chat-messages.component.html',
  styleUrls: ['./chat-messages.component.scss']
})
export class ChatMessagesComponent {

  @Input() messages: Message[] = [];
  @Input() isLoading = false;

  // ✅ URL BACKEND SANS /api (OBLIGATOIRE POUR LES IMAGES)
  backendUrl = environment.backendUrl;

  constructor(private sanitizer: DomSanitizer) {}

  // Sécurisé
  objectKeys(obj?: Record<string, string[]>): string[] {
    return obj ? Object.keys(obj) : [];
  }

  /**
   * Transforme le texte IA en HTML lisible
   */
  renderMessage(
    content: string | SafeHtml,
    isUser: boolean
  ): SafeHtml {

    if (!content) {
      return this.sanitizer.bypassSecurityTrustHtml('');
    }

    // ✅ déjà SafeHtml
    if (typeof content !== 'string') {
      return content;
    }

    // 🧑 Message utilisateur
    if (isUser) {
      return this.sanitizer.bypassSecurityTrustHtml(
        content.replace(/\n/g, '<br>')
      );
    }

    // 🤖 Message assistant
    let formatted = content
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;');

    // Titres avec emojis
    formatted = formatted.replace(
      /^(📚|🏫|📐|🖼️|ℹ️).*/gm,
      match => `<div class="section-title">${match}</div>`
    );

    // Listes "-"
    formatted = formatted.replace(/^- (.*)$/gm, '<li>$1</li>');
    formatted = formatted.replace(/(<li>.*<\/li>)/gs, '<ul>$1</ul>');

    formatted = formatted.replace(/\n/g, '<br>');

    return this.sanitizer.bypassSecurityTrustHtml(formatted);
  }
  // 🔍 Lightbox
selectedImage: string | null = null;

openImage(img: string) {
  this.selectedImage = this.backendUrl + img;
}

closeImage() {
  this.selectedImage = null;
}

// ⬇️ Télécharger
downloadImage(img: string) {
  const link = document.createElement('a');
  link.href = this.backendUrl + img;
  link.download = img.split('/').pop() || 'image.jpg';
  link.click();
}

}

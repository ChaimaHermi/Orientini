import { CommonModule } from '@angular/common';
import { Component, Input, Output, EventEmitter } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { DomSanitizer, SafeHtml } from '@angular/platform-browser';
import { Message } from '../../../../models/message.model';

@Component({
  selector: 'app-chat-messages',
  imports:[
    CommonModule, 
    FormsModule
  ],
  standalone: true,
  templateUrl: './chat-messages.component.html',
  styleUrls: ['./chat-messages.component.scss']
})
export class ChatMessagesComponent {
  @Input() messages: Message[] = [];
  @Input() isLoading = false;

  constructor(private sanitizer: DomSanitizer) {}

  safeHtml(content: string): SafeHtml {
    return this.sanitizer.bypassSecurityTrustHtml(content);
  }

}
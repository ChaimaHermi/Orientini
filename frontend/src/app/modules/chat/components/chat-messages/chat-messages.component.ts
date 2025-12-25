import { CommonModule } from '@angular/common';
import { Component, Input, Output, EventEmitter } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { DomSanitizer, SafeHtml } from '@angular/platform-browser';
import { FileSizePipe } from '../../pipes/file-size.pipe';
import { Message } from '../../../../models/message.model';

@Component({
  selector: 'app-chat-messages',
  imports:[
    CommonModule, 
    FormsModule,
    FileSizePipe
  ],
  standalone: true,
  templateUrl: './chat-messages.component.html',
  styleUrls: ['./chat-messages.component.scss']
})
export class ChatMessagesComponent {
  @Input() messages: Message[] = [];
  @Input() files: any[] = [];
  @Input() currentModel = 'Mistral';
  @Input() isLoading = false;
  @Output() viewFile = new EventEmitter<any>();

  constructor(private sanitizer: DomSanitizer) {}

  onViewFileClick(file: any) {
  this.viewFile.emit(file);
  }

  safeHtml(content: string): SafeHtml {
    return this.sanitizer.bypassSecurityTrustHtml(content);
  }

  isImage(file: any): boolean {
    return file.type.startsWith('image/');
  }
  
  getFilePreview(file: File): string {
    return URL.createObjectURL(file);
  }
}
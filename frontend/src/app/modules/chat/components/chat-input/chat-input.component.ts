import { CommonModule } from '@angular/common';
import { Component, ElementRef, EventEmitter, Input, Output, ViewChild } from '@angular/core';
import { FormsModule } from '@angular/forms';

@Component({
  selector: 'app-chat-input',
  imports: [
    CommonModule,
    FormsModule
  ],
  standalone: true,
  templateUrl: './chat-input.component.html',
  styleUrls: ['./chat-input.component.scss']
})
export class ChatInputComponent {
  @ViewChild('textarea') textarea!: ElementRef<HTMLTextAreaElement>;
  @Input() files: any[] = [];
  @Output() openFileUploader = new EventEmitter<void>();
  @Output() fileRemoved = new EventEmitter<any>();
  @Output() messageSent = new EventEmitter<string>();

  messageText = '';

  get hasFiles() {
    return this.files && this.files.length > 0;
  }

  emitOpenFileUploader() {
    this.openFileUploader.emit();
  }

  onEnter(event: any) {
    const keyboardEvent = event as KeyboardEvent;
    if (!keyboardEvent.shiftKey && this.messageText.trim()) {
      this.sendTextMessage();
      event.preventDefault();
    }
  }

  sendTextMessage() {
    const message = this.messageText.trim();
    if (message) {
      console.log('[chat-input] Message envoyé :', message);
      this.messageSent.emit(message);
      this.messageText = '';
    }
  }

  adjustTextareaHeight() {
    const textarea = this.textarea.nativeElement;
    textarea.style.height = 'auto';
    textarea.style.height = `${textarea.scrollHeight}px`;
    this.messageText = textarea.value;
  }

  emitRemoveFile(file: any) {
    this.fileRemoved.emit(file);
  }
}

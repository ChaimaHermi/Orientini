import { CommonModule } from '@angular/common';
import { Component, Input, Output, EventEmitter } from '@angular/core';
import { FormsModule } from '@angular/forms';

@Component({
  selector: 'app-file-viewer',
  imports:[
    CommonModule, 
    FormsModule
  ],
  standalone: true,
  templateUrl: './file-viewer.component.html',
  styleUrls: ['./file-viewer.component.scss']
})
export class FileViewerComponent {
  @Input() file: any = null;
  @Output() close = new EventEmitter<void>();

  get fileUrl() {
    return this.file ? URL.createObjectURL(this.file) : '';
  }

  get isImage(): boolean {
    return this.file?.type?.startsWith('image/') || false;
  }
}
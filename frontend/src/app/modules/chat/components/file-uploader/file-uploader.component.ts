import { CommonModule } from '@angular/common';
import { Component, EventEmitter, Output } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { FileSizePipe } from '../../pipes/file-size.pipe';

@Component({
  selector: 'app-file-uploader',
  imports:[
    CommonModule, 
    FormsModule,
    FileSizePipe
  ],
  standalone: true,
  templateUrl: './file-uploader.component.html',
  styleUrls: ['./file-uploader.component.scss']
})
export class FileUploaderComponent {
  @Output() fileUpload = new EventEmitter<any[]>();
  @Output() close = new EventEmitter<void>();

  files: any[] = [];
  isDragover = false;

  onDragOver(event: DragEvent) {
    event.preventDefault();
    event.stopPropagation();
    this.isDragover = true;
  }

  onDragLeave(event: DragEvent) {
    event.preventDefault();
    event.stopPropagation();
    this.isDragover = false;
  }

  onDrop(event: DragEvent) {
    event.preventDefault();
    event.stopPropagation();
    this.isDragover = false;
    
    if (event.dataTransfer?.files) {
      this.handleFiles(event.dataTransfer.files);
    }
  }

  onFileInputChange(event: Event) {
    const input = event.target as HTMLInputElement;
    if (input.files) {
      this.handleFiles(input.files);
    }
  }

  handleFiles(fileList: FileList) {
    for (let i = 0; i < fileList.length; i++) {
      const file = fileList.item(i);
      if (file) {
        this.files.push(file);
      }
    }
  }

  removeFile(index: number) {
    this.files.splice(index, 1);
  }

  uploadFiles() {
    this.fileUpload.emit(this.files);
    this.files = [];
  }
}
import { CommonModule } from '@angular/common';
import { Component, EventEmitter, Input, Output } from '@angular/core';
import { FormsModule } from '@angular/forms';

interface Model {
  id: string;
  name: string;
  description?: string;
}

@Component({
  selector: 'app-model-selector',
  imports:[
    CommonModule, 
    FormsModule
  ],
  standalone: true,
  templateUrl: './model-selector.component.html',
  styleUrls: ['./model-selector.component.scss']
})
export class ModelSelectorComponent {
  @Input() models: Model[] = [];
  @Input() selectedModel: Model | null = null;
  @Output() modelChange = new EventEmitter<Model>();

  isOpen = false;

  toggleDropdown() {
    this.isOpen = !this.isOpen;
  }

  closeDropdown() {
    this.isOpen = false;
  }

  selectModel(model: Model) {
    this.modelChange.emit(model);
    this.closeDropdown();
  }
}
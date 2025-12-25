import { SafeHtml } from '@angular/platform-browser';

export interface Message {
  id: string;
  content: string | SafeHtml;
  isUser: boolean;
  timestamp: Date;
  files?: File[];
  model_used?: string;
}

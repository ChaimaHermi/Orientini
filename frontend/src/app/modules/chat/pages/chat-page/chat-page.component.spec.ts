import { ComponentFixture, TestBed } from '@angular/core/testing';
import { HttpClientTestingModule } from '@angular/common/http/testing';

import { ChatPageComponent } from './chat-page.component';
import { ChatService } from '../../../../services/chat.service';

describe('ChatPageComponent', () => {
  let component: ChatPageComponent;
  let fixture: ComponentFixture<ChatPageComponent>;

  // 🔹 Mock simple du ChatService
  const chatServiceMock = {
    getConversations: () => ({ subscribe: () => {} }),
    getConversationMessages: () => ({ subscribe: () => {} }),
    sendQuestion: () => ({ subscribe: () => {} })
  };

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [
        ChatPageComponent,          // ✅ standalone component
        HttpClientTestingModule     // ✅ évite erreurs HTTP
      ],
      providers: [
        { provide: ChatService, useValue: chatServiceMock }
      ]
    }).compileComponents();

    fixture = TestBed.createComponent(ChatPageComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create the ChatPageComponent', () => {
    expect(component).toBeTruthy();
  });
});

import { Component, OnInit, OnDestroy, ViewChild, ElementRef, ChangeDetectorRef } from '@angular/core';
import { ChatService, PaperSummary } from './chat.service';
import { Subscription, interval } from 'rxjs';
import { switchMap, startWith } from 'rxjs/operators';

type MessageType = 'text' | 'results';

interface Message {
  from: 'user' | 'bot';
  type: MessageType;
  text?: string;
  results?: PaperSummary[];
}

@Component({
  selector: 'app-chat',
  templateUrl: './chatui.component.html',
  styles: [`
    /* Inline dark WhatsApp theme */
    :host { font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif; }
    .chat-wrapper {
      --bg-shell: #1e1e1e;
      --bg-chat: #2a2f32;
      --bg-bot: #2f3437;
      --bg-user: #005c4b;
      --bg-input: #262b2d;
      --text-light: #e1e1e1;
      --accent: #00a884;
      --border: #3a3f42;
      position: fixed;
      top: 50%; left: 50%;
      transform: translate(-50%, -50%);
      width: 360px; height: 600px;
      background: var(--bg-shell);
      border-radius: 12px;
      box-shadow: 0 6px 16px rgba(0,0,0,0.5);
      display: flex; flex-direction: column;
      overflow: hidden;
    }
    .chat-container {
      flex: 1;
      background: var(--bg-chat);
      padding: 12px;
      overflow-y: auto;
      -webkit-overflow-scrolling: touch;
    }
    .message { display: flex; margin-bottom: 10px; }
    .message.bot  { justify-content: flex-start; }
    .message.user { justify-content: flex-end; }
    .bubble {
      max-width: 75%; padding: 8px 12px; border-radius: 8px;
      line-height: 1.4; word-wrap: break-word; font-size: .95rem;
    }
    .bot .bubble  { background: var(--bg-bot); color: var(--text-light); border-top-left-radius: 0; }
    .user .bubble { background: var(--bg-user); color: var(--text-light); border-top-right-radius: 0; }
    .bubble.results { background: transparent; padding: 0; }
    .loading { font-style: italic; color: var(--text-light); margin-bottom: 6px; }
    .paper-card {
      background: var(--bg-bot);
      border-radius: 6px; padding: 8px; margin-bottom: 6px;
      box-shadow: 0 1px 2px rgba(0,0,0,0.4);
    }
    .paper-title {
      display: block; font-weight: 600; font-size: .95rem;
      color: var(--accent); text-decoration: none; margin-bottom: 4px;
    }
    .paper-title:hover { text-decoration: underline; }
    .paper-meta { font-size: .8em; color: #a0a0a0; margin-bottom: 6px; }
    .paper-summary { font-size: .9em; color: var(--text-light); margin: 0; }
    .input-area {
      display: flex; align-items: center; padding: 8px;
      background: var(--bg-input); border-top: 1px solid var(--border);
    }
    .input-area textarea {
      flex: 1; resize: none; border: none; outline: none;
      padding: 8px; border-radius: 6px; background: #32373a;
      color: var(--text-light); font-size: 1rem; margin-right: 8px;
    }
    .input-area textarea::-webkit-scrollbar { display: none; }
    .input-area button {
      padding: 8px 12px; border: none; border-radius: 6px;
      background: var(--accent); color: var(--bg-shell);
      font-weight: bold; cursor: pointer;
    }
    .input-area button:disabled { opacity: .5; cursor: not-allowed; }
  `]
})
export class ChatComponent implements OnInit, OnDestroy {
  @ViewChild('scrollContainer', { static: true }) private scrollContainer!: ElementRef;
  messages: Message[] = [];
  input = '';
  loading = false;

  private pollSub: Subscription | null = null;
  private lastResultMsgIdx: number | null = null;
  private POLL_INTERVAL = 30000;

  constructor(
    private chatService: ChatService,
    private cd: ChangeDetectorRef
  ) {}

  ngOnInit(): void {
    this.messages.push({ from: 'bot', type: 'text', text: `👋 Hi! I'm SCI-ML Bot. Ask me about physics research papers, and I'll fetch until you say "thanks".` });
    this.scrollToBottom();
  }

  sendMessage(): void {
    const query = this.input.trim(); if (!query) return;
    if (query.toLowerCase() === 'thanks') {
      this.stopPolling();
      this.messages.push({ from: 'user', type: 'text', text: query });
      this.messages.push({ from: 'bot', type: 'text', text: `🙏 You’re welcome!` });
      this.input = '';
      this.scrollToBottom(); return;
    }

    this.stopPolling();
    this.messages.push({ from: 'user', type: 'text', text: query });
    this.loading = true;
    this.messages.push({ from: 'bot', type: 'results', results: [] });
    this.lastResultMsgIdx = this.messages.length - 1;
    this.cd.detectChanges(); this.scrollToBottom();

    this.pollSub = interval(this.POLL_INTERVAL).pipe(
      startWith(0), switchMap(() => this.chatService.search(query))
    ).subscribe(
      papers => {
        if (this.lastResultMsgIdx === null) return;
        this.loading = false;
        this.messages[this.lastResultMsgIdx].results = papers;
        this.cd.detectChanges(); this.scrollToBottom();
      }, err => {
        console.error(err); this.stopPolling();
        this.messages.push({ from: 'bot', type: 'text', text: '🚨 Error. Polling stopped.' });
      }
    );
    this.input = '';
  }

  onEnter(e: KeyboardEvent): void {
    if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); this.sendMessage(); }
  }

  private stopPolling() {
    this.pollSub?.unsubscribe(); this.pollSub = null; this.lastResultMsgIdx = null;
  }

  private scrollToBottom(): void {
    setTimeout(() => {
      const el = this.scrollContainer.nativeElement;
      el.scrollTop = el.scrollHeight;
    }, 50);
  }

  ngOnDestroy(): void { this.stopPolling(); }
}
// src/app/chat/chat.service.ts
import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../../environments/environment';

export interface PaperSummary {
  title: string;
  abstract: string;
  authors: string[];
  link: string;
  arxiv_id: string;
  score: number;       // ← new
}

@Injectable({ providedIn: 'root' })
export class ChatService {
  private base = environment.apiUrl;

  constructor(private http: HttpClient) {}

  search(
    query: string,
    top: number = 5,
    minScore: number = 0    // ← optional threshold
  ): Observable<PaperSummary[]> {
    return this.http.get<PaperSummary[]>(`${this.base}/search/`, {
      params: {
        query,
        top:    top.toString(),
        min_score: minScore.toString()   // ← pass it if you want
      }
    });
  }
}

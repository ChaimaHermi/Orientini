import { Injectable } from '@angular/core';
import { BehaviorSubject } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class SharedService {

  private tokenKey = 'auth_token';
  private rememberMeKey = 'remember_me';

  private tokenSubject = new BehaviorSubject<string | null>(this.getToken());
  private rememberMeSubject = new BehaviorSubject<boolean>(this.getRememberMe());

  /** Sauvegarde token + rememberMe */
  storeAuthInfo(token: string, rememberMe: boolean): void {
    localStorage.setItem(this.tokenKey, token);
    localStorage.setItem(this.rememberMeKey, rememberMe.toString());

    this.tokenSubject.next(token);
    this.rememberMeSubject.next(rememberMe);
  }

  /** Supprime toutes les infos d’auth */
  clearAuthInfo(): void {
    localStorage.removeItem(this.tokenKey);
    localStorage.removeItem(this.rememberMeKey);

    this.tokenSubject.next(null);
    this.rememberMeSubject.next(false);
  }

  /** Récupération du token */
  getToken(): string | null {
    return localStorage.getItem(this.tokenKey);
  }

  /** Récupération remember me */
  getRememberMe(): boolean {
    return localStorage.getItem(this.rememberMeKey) === 'true';
  }

  /** Observables (optionnel, pour state global) */
  token$ = this.tokenSubject.asObservable();
  rememberMe$ = this.rememberMeSubject.asObservable();
}

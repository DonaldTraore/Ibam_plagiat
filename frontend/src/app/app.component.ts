import { Component } from '@angular/core';
import { AuthService } from './services/auth.service';

@Component({
  selector: 'app-root',
  template: `
    <div class="app-container">
      <app-navbar *ngIf="authService.getCurrentUserValue()"></app-navbar>
      <mat-sidenav-container class="sidenav-container" *ngIf="authService.getCurrentUserValue()">
        <mat-sidenav mode="side" opened class="sidenav">
          <app-sidebar></app-sidebar>
        </mat-sidenav>
        <mat-sidenav-content>
          <main class="main-content">
            <router-outlet></router-outlet>
          </main>
          <app-footer></app-footer>
        </mat-sidenav-content>
      </mat-sidenav-container>
      <div *ngIf="!authService.getCurrentUserValue()" class="auth-container">
        <router-outlet></router-outlet>
      </div>
    </div>
  `,
  styles: [`
    .app-container {
      display: flex;
      flex-direction: column;
      height: 100vh;
    }
    .sidenav-container {
      flex: 1;
    }
    .sidenav {
      width: 250px;
      background: #f5f5f5;
    }
    .main-content {
      padding: 20px;
      min-height: calc(100vh - 130px);
    }
    .auth-container {
      height: 100vh;
      display: flex;
      align-items: center;
      justify-content: center;
      background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
  `]
})
export class AppComponent {
  title = 'Système de Détection de Plagiat';

  constructor(public authService: AuthService) {
    // Nettoyer les tokens expirés au démarrage
    const token = localStorage.getItem('access_token');
    if (token) {
      try {
        const decoded: any = JSON.parse(atob(token.split('.')[1]));
        if (decoded.exp && decoded.exp * 1000 < Date.now()) {
          console.log('Token expiré, nettoyage...');
          localStorage.removeItem('access_token');
          localStorage.removeItem('refresh_token');
        }
      } catch {
        console.log('Token invalide, nettoyage...');
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
      }
    }
  }
}

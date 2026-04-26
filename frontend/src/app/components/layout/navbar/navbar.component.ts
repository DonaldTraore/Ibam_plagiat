import { Component } from '@angular/core';
import { Router } from '@angular/router';
import { Observable } from 'rxjs';
import { AuthService } from '../../../services/auth.service';

@Component({
  selector: 'app-navbar',
  template: `
    <mat-toolbar color="primary" class="navbar">
      <div class="navbar-left">
        <span class="brand">
          <mat-icon>school</mat-icon>
          <span class="brand-text">Plagiat IBAM</span>
        </span>
      </div>

      <div class="navbar-right" *ngIf="user$ | async as user">
        <button mat-icon-button [matMenuTriggerFor]="notificationsMenu">
          <mat-icon [matBadge]="0" matBadgeColor="warn" matBadgeSize="small" [matBadgeHidden]="true">notifications</mat-icon>
        </button>
        <mat-menu #notificationsMenu="matMenu">
          <div class="notification-menu">
            <h4>Notifications</h4>
            <mat-divider></mat-divider>
            <p class="no-notifications">Pas de nouvelles notifications</p>
          </div>
        </mat-menu>

        <button mat-button [matMenuTriggerFor]="userMenu" class="user-menu-button">
          <mat-icon>account_circle</mat-icon>
          <span class="hide-mobile">{{ user.first_name }} {{ user.last_name }}</span>
          <mat-icon>arrow_drop_down</mat-icon>
        </button>
        <mat-menu #userMenu="matMenu">
          <div class="user-info">
            <p><strong>{{ user.first_name }} {{ user.last_name }}</strong></p>
            <p class="user-role">{{ user.role }}</p>
          </div>
          <mat-divider></mat-divider>
          <button mat-menu-item (click)="logout()">
            <mat-icon>logout</mat-icon>
            <span>Déconnexion</span>
          </button>
        </mat-menu>
      </div>
    </mat-toolbar>
  `,
  styles: [`
    .navbar {
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding: 0 20px;
    }
    .brand {
      display: flex;
      align-items: center;
      gap: 10px;
      font-size: 20px;
      font-weight: 500;
    }
    .navbar-right {
      display: flex;
      align-items: center;
      gap: 10px;
    }
    .user-menu-button {
      display: flex;
      align-items: center;
      gap: 5px;
    }
    .notification-menu {
      padding: 10px;
      min-width: 250px;
    }
    .notification-menu h4 {
      margin: 0 0 10px 0;
    }
    .no-notifications {
      color: #999;
      text-align: center;
      padding: 20px;
      margin: 0;
    }
    .user-info {
      padding: 10px 15px;
    }
    .user-info p {
      margin: 0;
    }
    .user-role {
      color: #666;
      font-size: 12px;
      text-transform: uppercase;
    }
    @media (max-width: 768px) {
      .hide-mobile {
        display: none;
      }
    }
  `]
})
export class NavbarComponent {
  user$: Observable<any>;

  constructor(
    private authService: AuthService,
    private router: Router
  ) {
    this.user$ = this.authService.currentUser$;
  }

  logout(): void {
    this.authService.logout();
  }
}

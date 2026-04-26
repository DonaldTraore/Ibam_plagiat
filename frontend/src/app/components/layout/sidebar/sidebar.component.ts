import { Component } from '@angular/core';
import { Observable } from 'rxjs';
import { AuthService } from '../../../services/auth.service';

interface MenuItem {
  icon: string;
  label: string;
  route: string;
  roles?: string[];
}

@Component({
  selector: 'app-sidebar',
  template: `
    <mat-list class="sidebar-menu" *ngIf="user$ | async as user">
      <div class="menu-section">
        <h3 mat-subheader>Principal</h3>
        <a mat-list-item *ngFor="let item of getMenuItems(user.role)" 
           [routerLink]="item.route" routerLinkActive="active-link">
          <mat-icon mat-list-icon>{{ item.icon }}</mat-icon>
          <span mat-line>{{ item.label }}</span>
        </a>
      </div>

      <mat-divider></mat-divider>

      <div class="menu-section" *ngIf="user.role === 'ETUDIANT'">
        <h3 mat-subheader>Mes Documents</h3>
        <a mat-list-item routerLink="/reports/my-tests" routerLinkActive="active-link">
          <mat-icon mat-list-icon>science</mat-icon>
          <span mat-line>Tests privés</span>
        </a>
      </div>

      <mat-divider></mat-divider>

      <div class="menu-section">
        <h3 mat-subheader>Informations</h3>
        <a mat-list-item routerLink="/history" routerLinkActive="active-link">
          <mat-icon mat-list-icon>history</mat-icon>
          <span mat-line>Historique</span>
        </a>
        <a mat-list-item routerLink="/notifications" routerLinkActive="active-link">
          <mat-icon mat-list-icon>notifications</mat-icon>
          <span mat-line>Notifications</span>
        </a>
      </div>

      <mat-divider></mat-divider>

      <div class="menu-section" *ngIf="isAdmin(user.role)">
        <h3 mat-subheader>Administration</h3>
        <a mat-list-item routerLink="/admin/users" routerLinkActive="active-link">
          <mat-icon mat-list-icon>people</mat-icon>
          <span mat-line>Utilisateurs</span>
        </a>
      </div>
    </mat-list>
  `,
  styles: [`
    .sidebar-menu {
      padding-top: 0;
    }
    .menu-section {
      margin-bottom: 10px;
    }
    .menu-section h3 {
      font-size: 12px;
      text-transform: uppercase;
      color: #666;
      padding: 15px 16px 5px;
      margin: 0;
    }
    mat-list-item {
      cursor: pointer;
    }
    .active-link {
      background-color: #e3f2fd;
      color: #1976d2;
    }
    mat-icon {
      color: #666;
    }
    .active-link mat-icon {
      color: #1976d2;
    }
  `]
})
export class SidebarComponent {
  user$: Observable<any>;

  menuItems: MenuItem[] = [
    { icon: 'dashboard', label: 'Tableau de bord', route: '/dashboard' },
    { icon: 'description', label: 'Rapports', route: '/reports' },
    { icon: 'topic', label: 'Thèmes', route: '/themes' },
    { icon: 'folder', label: 'Documents', route: '/documents', roles: ['SECRETAIRE', 'CHEF_DEPARTEMENT', 'DA'] },
  ];

  constructor(private authService: AuthService) {
    this.user$ = this.authService.currentUser$;
  }

  getMenuItems(userRole: string): MenuItem[] {
    return this.menuItems.filter(item => 
      !item.roles || item.roles.includes(userRole)
    );
  }

  isAdmin(role: string): boolean {
    return role === 'ADMIN' || role === 'DA';
  }
}

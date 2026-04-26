import { Component } from '@angular/core';
import { Observable } from 'rxjs';
import { AuthService } from '../../../services/auth.service';

@Component({
  selector: 'app-sidebar',
  template: `
    <mat-list class="sidebar-menu" *ngIf="user$ | async as user">
      <!-- MENU ÉTUDIANT -->
      <ng-container *ngIf="user.role === 'ETUDIANT'">
        <div class="menu-section">
          <h3 mat-subheader>Principal</h3>
          <a mat-list-item routerLink="/dashboard" routerLinkActive="active-link">
            <mat-icon mat-list-icon>dashboard</mat-icon>
            <span mat-line>Tableau de bord</span>
          </a>
        </div>

        <mat-divider></mat-divider>

        <div class="menu-section">
          <h3 mat-subheader>Mes Actions</h3>
          <a mat-list-item routerLink="/reports/private-test" routerLinkActive="active-link">
            <mat-icon mat-list-icon>science</mat-icon>
            <span mat-line>Test Privé</span>
          </a>
          <a mat-list-item routerLink="/themes/submit" routerLinkActive="active-link">
            <mat-icon mat-list-icon>add_circle</mat-icon>
            <span mat-line>Proposer un Thème</span>
          </a>
          <a mat-list-item routerLink="/reports/my-submissions" routerLinkActive="active-link">
            <mat-icon mat-list-icon>folder</mat-icon>
            <span mat-line>Mes Soumissions</span>
          </a>
        </div>
      </ng-container>

      <!-- MENU CHEF DE DÉPARTEMENT -->
      <ng-container *ngIf="user.role === 'CHEF_DEPARTEMENT'">
        <div class="menu-section">
          <h3 mat-subheader>Principal</h3>
          <a mat-list-item routerLink="/dashboard" routerLinkActive="active-link">
            <mat-icon mat-list-icon>dashboard</mat-icon>
            <span mat-line>Tableau de bord</span>
          </a>
        </div>

        <mat-divider></mat-divider>

        <div class="menu-section">
          <h3 mat-subheader>À Traiter</h3>
          <a mat-list-item routerLink="/reports/pending" routerLinkActive="active-link">
            <mat-icon mat-list-icon>description</mat-icon>
            <span mat-line>Rapports à Traiter</span>
          </a>
          <a mat-list-item routerLink="/themes/pending" routerLinkActive="active-link">
            <mat-icon mat-list-icon>topic</mat-icon>
            <span mat-line>Thèmes à Traiter</span>
          </a>
        </div>
      </ng-container>

      <!-- MENU DA -->
      <ng-container *ngIf="user.role === 'DA'">
        <div class="menu-section">
          <h3 mat-subheader>Principal</h3>
          <a mat-list-item routerLink="/dashboard" routerLinkActive="active-link">
            <mat-icon mat-list-icon>dashboard</mat-icon>
            <span mat-line>Tableau de bord</span>
          </a>
        </div>

        <mat-divider></mat-divider>

        <div class="menu-section">
          <h3 mat-subheader>Validation Finale</h3>
          <a mat-list-item routerLink="/reports/final-validation" routerLinkActive="active-link">
            <mat-icon mat-list-icon>verified</mat-icon>
            <span mat-line>Validation Finale Rapports</span>
          </a>
          <a mat-list-item routerLink="/themes/final-validation" routerLinkActive="active-link">
            <mat-icon mat-list-icon>gavel</mat-icon>
            <span mat-line>Validation Finale Thèmes</span>
          </a>
        </div>
      </ng-container>

      <!-- MENU SECRÉTAIRE -->
      <ng-container *ngIf="user.role === 'SECRETAIRE'">
        <div class="menu-section">
          <h3 mat-subheader>Principal</h3>
          <a mat-list-item routerLink="/dashboard" routerLinkActive="active-link">
            <mat-icon mat-list-icon>dashboard</mat-icon>
            <span mat-line>Tableau de bord</span>
          </a>
        </div>

        <mat-divider></mat-divider>

        <div class="menu-section">
          <h3 mat-subheader>Gestion Documents</h3>
          <a mat-list-item routerLink="/documents/upload" routerLinkActive="active-link">
            <mat-icon mat-list-icon>upload_file</mat-icon>
            <span mat-line>Ajouter Document</span>
          </a>
          <a mat-list-item routerLink="/documents" routerLinkActive="active-link">
            <mat-icon mat-list-icon>folder</mat-icon>
            <span mat-line>Documents</span>
          </a>
        </div>
      </ng-container>

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

  constructor(private authService: AuthService) {
    this.user$ = this.authService.currentUser$;
  }
}

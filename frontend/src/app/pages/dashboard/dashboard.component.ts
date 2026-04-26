import { Component, OnInit } from '@angular/core';
import { Observable } from 'rxjs';
import { AuthService } from '../../services/auth.service';

@Component({
  selector: 'app-dashboard',
  template: `
    <div class="dashboard">
      <h1>Tableau de bord</h1>
      
      <div *ngIf="user$ | async as user">
        <mat-card class="welcome-card">
          <mat-card-content>
            <h2>Bienvenue, {{ user.first_name }} {{ user.last_name }}!</h2>
            <p>Vous êtes connecté en tant que <strong>{{ user.role }}</strong></p>
          </mat-card-content>
        </mat-card>

        <!-- Statistiques pour le Chef - à 0 au départ -->
        <div *ngIf="user.role === 'CHEF_DEPARTEMENT'" class="stats-grid">
          <mat-card class="stat-card">
            <mat-card-content>
              <mat-icon class="stat-icon blue">description</mat-icon>
              <div class="stat-info">
                <h3>Rapports à Traiter</h3>
                <p class="stat-number">0</p>
              </div>
            </mat-card-content>
          </mat-card>

          <mat-card class="stat-card">
            <mat-card-content>
              <mat-icon class="stat-icon orange">topic</mat-icon>
              <div class="stat-info">
                <h3>Thèmes à Traiter</h3>
                <p class="stat-number">0</p>
              </div>
            </mat-card-content>
          </mat-card>
        </div>

        <!-- Actions rapides -->
        <mat-card class="quick-actions">
          <mat-card-header>
            <mat-card-title>Actions rapides</mat-card-title>
          </mat-card-header>
          <mat-card-content>
            <div class="action-buttons">
              <!-- Actions ÉTUDIANT -->
              <button mat-raised-button color="primary" routerLink="/reports/private-test" *ngIf="user.role === 'ETUDIANT'">
                <mat-icon>science</mat-icon>
                Test Privé
              </button>
              <button mat-raised-button color="accent" routerLink="/themes/submit" *ngIf="user.role === 'ETUDIANT'">
                <mat-icon>add_circle</mat-icon>
                Proposer Thème
              </button>

              <!-- Actions CHEF -->
              <button mat-raised-button color="primary" routerLink="/reports/pending" *ngIf="user.role === 'CHEF_DEPARTEMENT'">
                <mat-icon>visibility</mat-icon>
                Voir Rapports à Traiter
              </button>
              <button mat-raised-button color="accent" routerLink="/themes/pending" *ngIf="user.role === 'CHEF_DEPARTEMENT'">
                <mat-icon>topic</mat-icon>
                Voir Thèmes à Traiter
              </button>

              <!-- Actions DA -->
              <button mat-raised-button color="primary" routerLink="/reports/final-validation" *ngIf="user.role === 'DA'">
                <mat-icon>verified</mat-icon>
                Validation Finale
              </button>

              <!-- Actions SECRÉTAIRE -->
              <button mat-raised-button color="primary" routerLink="/documents/upload" *ngIf="user.role === 'SECRETAIRE'">
                <mat-icon>upload_file</mat-icon>
                Ajouter Document
              </button>
            </div>
          </mat-card-content>
        </mat-card>
      </div>
    </div>
  `,
  styles: [`
    .dashboard {
      padding: 20px;
    }
    h1 {
      margin-bottom: 20px;
      color: #333;
    }
    .welcome-card {
      margin-bottom: 20px;
      background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
      color: white;
    }
    .welcome-card h2 {
      margin: 0;
      font-size: 24px;
    }
    .welcome-card p {
      margin: 10px 0 0 0;
      opacity: 0.9;
    }
    .stats-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
      gap: 20px;
      margin-bottom: 20px;
    }
    .stat-card mat-card-content {
      display: flex;
      align-items: center;
      gap: 15px;
    }
    .stat-icon {
      font-size: 48px;
      width: 48px;
      height: 48px;
    }
    .stat-icon.blue { color: #2196f3; }
    .stat-icon.green { color: #4caf50; }
    .stat-icon.orange { color: #ff9800; }
    .stat-icon.red { color: #f44336; }
    .stat-icon.purple { color: #9c27b0; }
    .stat-info h3 {
      margin: 0;
      font-size: 14px;
      color: #666;
    }
    .stat-number {
      margin: 5px 0 0 0;
      font-size: 28px;
      font-weight: bold;
      color: #333;
    }
    .quick-actions {
      margin-top: 20px;
    }
    .action-buttons {
      display: flex;
      gap: 10px;
      flex-wrap: wrap;
    }
    @media (max-width: 600px) {
      .stats-grid {
        grid-template-columns: 1fr;
      }
    }
  `]
})
export class DashboardComponent implements OnInit {
  user$: Observable<any>;

  constructor(private authService: AuthService) {
    this.user$ = this.authService.currentUser$;
  }

  ngOnInit(): void {
    // Charger les statistiques réelles ici
  }
}

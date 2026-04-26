import { Component, OnInit } from '@angular/core';
import { MatSnackBar } from '@angular/material/snack-bar';
import { HttpClient } from '@angular/common/http';
import { environment } from '../../../../environments/environment';

interface HistoryItem {
  id: number;
  type: 'TEST_PRIVE' | 'THEME_SOUMIS' | 'RAPPORT_SOUMIS';
  titre: string;
  date: string;
  statut: string;
  details?: string;
}

@Component({
  selector: 'app-history-list',
  template: `
    <div class="history-list">
      <h2>Historique de mes activités</h2>

      <div *ngIf="loading" class="loading">
        <mat-spinner diameter="40"></mat-spinner>
        <p>Chargement de l'historique...</p>
      </div>

      <div *ngIf="!loading && historyItems.length === 0" class="empty-state">
        <mat-icon class="empty-icon">history</mat-icon>
        <p>Aucune activité enregistrée pour le moment.</p>
        <p class="hint">Vos tests privés et soumissions de thèmes apparaîtront ici.</p>
      </div>

      <mat-accordion *ngIf="!loading && historyItems.length > 0" multi="true">
        <mat-expansion-panel *ngFor="let item of historyItems" [expanded]="true">
          <mat-expansion-panel-header>
            <mat-panel-title>
              <mat-icon [color]="getIconColor(item.type)">
                {{ getIcon(item.type) }}
              </mat-icon>
              <span class="item-title">{{ item.titre }}</span>
            </mat-panel-title>
            <mat-panel-description>
              {{ formatDate(item.date) }}
              <span class="statut-badge" [class]="item.statut.toLowerCase()">
                {{ item.statut }}
              </span>
            </mat-panel-description>
          </mat-expansion-panel-header>

          <div class="item-details">
            <p><strong>Type :</strong> {{ getTypeLabel(item.type) }}</p>
            <p *ngIf="item.details"><strong>Détails :</strong> {{ item.details }}</p>
          </div>
        </mat-expansion-panel>
      </mat-accordion>
    </div>
  `,
  styles: [`
    .history-list {
      padding: 20px;
      max-width: 900px;
      margin: 0 auto;
    }
    h2 {
      margin-bottom: 30px;
      color: #333;
    }
    .loading {
      display: flex;
      flex-direction: column;
      align-items: center;
      gap: 15px;
      padding: 40px;
    }
    .empty-state {
      text-align: center;
      padding: 60px 20px;
      color: #666;
    }
    .empty-icon {
      font-size: 64px;
      width: 64px;
      height: 64px;
      color: #ccc;
      margin-bottom: 20px;
    }
    .hint {
      font-size: 14px;
      color: #999;
      margin-top: 10px;
    }
    mat-expansion-panel {
      margin-bottom: 10px;
    }
    mat-panel-title mat-icon {
      margin-right: 10px;
    }
    .item-title {
      font-weight: 500;
    }
    .statut-badge {
      margin-left: 10px;
      padding: 2px 8px;
      border-radius: 12px;
      font-size: 12px;
      font-weight: 500;
    }
    .statut-badge.soumis,
    .statut-badge.en_attente {
      background: #fff3e0;
      color: #e65100;
    }
    .statut-badge.validé,
    .statut-badge.validé_par_chef,
    .statut-badge.validé_par_da {
      background: #e8f5e9;
      color: #2e7d32;
    }
    .statut-badge.rejeté,
    .statut-badge.rejeté_par_chef,
    .statut-badge.rejeté_par_da {
      background: #ffebee;
      color: #c62828;
    }
    .statut-badge.test_privé {
      background: #e3f2fd;
      color: #1565c0;
    }
    .item-details {
      padding: 10px 0;
    }
    .item-details p {
      margin: 5px 0;
      color: #555;
    }
  `]
})
export class HistoryListComponent implements OnInit {
  historyItems: HistoryItem[] = [];
  loading = true;

  private apiUrl = environment.apiUrl;

  constructor(
    private http: HttpClient,
    private snackBar: MatSnackBar
  ) {}

  ngOnInit(): void {
    this.loadHistory();
  }

  loadHistory(): void {
    this.loading = true;

    // Appel API pour récupérer l'historique
    this.http.get<HistoryItem[]>(`${this.apiUrl}/history/my-history/`).subscribe({
      next: (items) => {
        this.historyItems = items;
        this.loading = false;
      },
      error: () => {
        this.loading = false;
        // Données de test si l'API n'est pas prête
        this.historyItems = [
          {
            id: 1,
            type: 'TEST_PRIVE',
            titre: 'Test plagiat - Mémoire Finance',
            date: new Date().toISOString(),
            statut: 'Test Privé',
            details: 'Score de plagiat: 12% - Le document est original'
          },
          {
            id: 2,
            type: 'THEME_SOUMIS',
            titre: 'Détection de plagiat par intelligence artificielle',
            date: new Date(Date.now() - 86400000).toISOString(),
            statut: 'Soumis',
            details: 'En attente de validation par le Chef de Département'
          }
        ];
      }
    });
  }

  getIcon(type: string): string {
    switch (type) {
      case 'TEST_PRIVE': return 'science';
      case 'THEME_SOUMIS': return 'topic';
      case 'RAPPORT_SOUMIS': return 'description';
      default: return 'history';
    }
  }

  getIconColor(type: string): string {
    switch (type) {
      case 'TEST_PRIVE': return 'primary';
      case 'THEME_SOUMIS': return 'accent';
      case 'RAPPORT_SOUMIS': return 'warn';
      default: return '';
    }
  }

  getTypeLabel(type: string): string {
    switch (type) {
      case 'TEST_PRIVE': return 'Test Privé de Plagiat';
      case 'THEME_SOUMIS': return 'Soumission de Thème';
      case 'RAPPORT_SOUMIS': return 'Soumission de Rapport';
      default: return type;
    }
  }

  formatDate(dateString: string): string {
    const date = new Date(dateString);
    return date.toLocaleDateString('fr-FR', {
      day: '2-digit',
      month: 'short',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  }
}

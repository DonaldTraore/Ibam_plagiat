import { Component, OnInit } from '@angular/core';
import { ActivatedRoute } from '@angular/router';
import { ReportService, ReportDetail } from '../../../services/report.service';
import { MatSnackBar } from '@angular/material/snack-bar';

@Component({
  selector: 'app-report-detail',
  template: `
    <div class="report-detail" *ngIf="report">
      <mat-card>
        <mat-card-header>
          <mat-card-title>{{ report.titre }}</mat-card-title>
          <mat-card-subtitle>
            {{ report.type_document_display }} - Par {{ report.etudiant?.first_name }} {{ report.etudiant?.last_name }}
          </mat-card-subtitle>
        </mat-card-header>

        <mat-card-content>
          <div class="info-section">
            <h3>Informations</h3>
            <p><strong>Statut:</strong> <span [style.color]="report.statut_color">{{ report.statut_display }}</span></p>
            <p><strong>Département:</strong> {{ report.departement }}</p>
            <p><strong>Nombre de pages:</strong> {{ report.nombre_pages || 'Non calculé' }}</p>
            <p><strong>Nombre de mots:</strong> {{ report.nombre_mots || 'Non calculé' }}</p>
          </div>

          <mat-divider></mat-divider>

          <div class="plagiarism-section">
            <h3>Résultat de Détection de Plagiat</h3>
            <div class="score-display" [class]="getScoreClass(report.score_plagiat_global)">
              <span class="score-value">{{ report.score_plagiat_global }}%</span>
              <span class="score-label">de similarité détectée</span>
            </div>

            <div class="actions" *ngIf="!report.est_plagiat || report.score_plagiat_global < 25">
              <span class="status-badge acceptable">Rapport acceptable</span>
            </div>
            <div class="actions" *ngIf="report.est_plagiat">
              <span class="status-badge plagiarism">Plagiat détecté - Attention</span>
            </div>
          </div>

          <mat-divider></mat-divider>

          <div class="file-section">
            <h3>Fichier</h3>
            <a mat-raised-button [href]="report.fichier" target="_blank">
              <mat-icon>download</mat-icon> Télécharger le rapport
            </a>
          </div>

          <div class="validation-section" *ngIf="report.statut !== 'BROUILLON'">
            <h3>Validation</h3>
            <p *ngIf="report.valide_par_chef">
              <mat-icon color="primary">check_circle</mat-icon>
              Validé par le Chef de département le {{ report.date_validation_chef | date }}
            </p>
            <p *ngIf="report.valide_par_da">
              <mat-icon color="primary">check_circle</mat-icon>
              Validé définitivement par le DA le {{ report.date_validation_da | date }}
            </p>
            <p *ngIf="report.motif_rejet">
              <mat-icon color="warn">cancel</mat-icon>
              Rejeté: {{ report.motif_rejet }}
            </p>
          </div>
        </mat-card-content>

        <mat-card-actions>
          <button mat-raised-button color="primary" (click)="testPlagiarism()" 
                  *ngIf="canTestPlagiarism()">
            <mat-icon>search</mat-icon> Tester le Plagiat
          </button>
          <button mat-raised-button color="accent" (click)="submitReport()" 
                  *ngIf="canSubmit()">
            <mat-icon>send</mat-icon> Soumettre
          </button>
        </mat-card-actions>
      </mat-card>
    </div>
  `,
  styles: [`
    .report-detail {
      padding: 20px;
      max-width: 800px;
      margin: 0 auto;
    }
    .info-section, .plagiarism-section, .file-section, .validation-section {
      margin: 20px 0;
    }
    h3 {
      color: #333;
      margin-bottom: 15px;
    }
    .score-display {
      display: flex;
      flex-direction: column;
      align-items: center;
      padding: 20px;
      border-radius: 8px;
      margin: 15px 0;
    }
    .score-display.plagiat-low {
      background: #e8f5e9;
      color: #2e7d32;
    }
    .score-display.plagiat-medium {
      background: #fff3e0;
      color: #ef6c00;
    }
    .score-display.plagiat-high {
      background: #ffebee;
      color: #c62828;
    }
    .score-value {
      font-size: 48px;
      font-weight: bold;
    }
    .score-label {
      font-size: 14px;
      margin-top: 5px;
    }
    .actions {
      margin-top: 15px;
      text-align: center;
    }
    .status-badge {
      display: inline-block;
      padding: 8px 16px;
      border-radius: 16px;
      font-weight: 500;
      font-size: 14px;
    }
    .status-badge.acceptable {
      background: #e3f2fd;
      color: #1976d2;
    }
    .status-badge.plagiarism {
      background: #ffebee;
      color: #c62828;
    }
    mat-card-actions {
      display: flex;
      gap: 10px;
      padding: 16px;
    }
    mat-icon {
      vertical-align: middle;
    }
  `]
})
export class ReportDetailComponent implements OnInit {
  report: ReportDetail | null = null;
  reportId: number = 0;

  constructor(
    private route: ActivatedRoute,
    private reportService: ReportService,
    private snackBar: MatSnackBar
  ) {}

  ngOnInit(): void {
    this.reportId = +this.route.snapshot.paramMap.get('id')!;
    this.loadReport();
  }

  loadReport(): void {
    this.reportService.getReport(this.reportId).subscribe({
      next: (report) => {
        this.report = report;
      },
      error: () => {
        this.snackBar.open('Erreur lors du chargement du rapport', 'Fermer', { duration: 3000 });
      }
    });
  }

  getScoreClass(score: number): string {
    if (score < 15) return 'plagiat-low';
    if (score < 25) return 'plagiat-medium';
    return 'plagiat-high';
  }

  canTestPlagiarism(): boolean {
    return true; // Implémenter la logique selon le rôle
  }

  canSubmit(): boolean {
    return this.report?.statut === 'BROUILLON' || this.report?.statut === 'REJETE_CHEF';
  }

  testPlagiarism(): void {
    this.reportService.testPlagiarism(this.reportId).subscribe({
      next: (result) => {
        this.snackBar.open('Test de plagiat terminé !', 'Fermer', { duration: 3000 });
        this.loadReport();
      },
      error: () => {
        this.snackBar.open('Erreur lors du test', 'Fermer', { duration: 3000 });
      }
    });
  }

  submitReport(): void {
    this.reportService.submitReport(this.reportId).subscribe({
      next: () => {
        this.snackBar.open('Rapport soumis avec succès !', 'Fermer', { duration: 3000 });
        this.loadReport();
      },
      error: () => {
        this.snackBar.open('Erreur lors de la soumission', 'Fermer', { duration: 3000 });
      }
    });
  }
}

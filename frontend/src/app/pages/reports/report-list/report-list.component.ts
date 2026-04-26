import { Component, OnInit } from '@angular/core';
import { MatDialog } from '@angular/material/dialog';
import { MatSnackBar } from '@angular/material/snack-bar';
import { ReportService, Report } from '../../../services/report.service';
import { AuthService } from '../../../services/auth.service';
import { Observable } from 'rxjs';

@Component({
  selector: 'app-report-list',
  template: `
    <div class="report-list">
      <div class="header">
        <h1>Liste des Rapports</h1>
        <button mat-raised-button color="primary" routerLink="/reports/create" 
                *ngIf="user?.role === 'ETUDIANT'">
          <mat-icon>add</mat-icon> Nouveau Rapport
        </button>
      </div>

      <mat-table [dataSource]="reports" class="mat-elevation-z2">
        <!-- Titre Column -->
        <ng-container matColumnDef="titre">
          <mat-header-cell *matHeaderCellDef>Titre</mat-header-cell>
          <mat-cell *matCellDef="let report">{{ report.titre }}</mat-cell>
        </ng-container>

        <!-- Type Column -->
        <ng-container matColumnDef="type">
          <mat-header-cell *matHeaderCellDef>Type</mat-header-cell>
          <mat-cell *matCellDef="let report">{{ report.type_document_display }}</mat-cell>
        </ng-container>

        <!-- Auteur Column -->
        <ng-container matColumnDef="auteur">
          <mat-header-cell *matHeaderCellDef>Auteur</mat-header-cell>
          <mat-cell *matCellDef="let report">
            {{ report.etudiant?.first_name }} {{ report.etudiant?.last_name }}
          </mat-cell>
        </ng-container>

        <!-- Statut Column -->
        <ng-container matColumnDef="statut">
          <mat-header-cell *matHeaderCellDef>Statut</mat-header-cell>
          <mat-cell *matCellDef="let report">
            <span [style.color]="report.statut_color">{{ report.statut_display }}</span>
          </mat-cell>
        </ng-container>

        <!-- Score Column -->
        <ng-container matColumnDef="score">
          <mat-header-cell *matHeaderCellDef>Plagiat</mat-header-cell>
          <mat-cell *matCellDef="let report">
            <span [class]="getScoreClass(report.score_plagiat_global)">
              {{ report.score_plagiat_global }}%
            </span>
          </mat-cell>
        </ng-container>

        <!-- Date Column -->
        <ng-container matColumnDef="date">
          <mat-header-cell *matHeaderCellDef>Date</mat-header-cell>
          <mat-cell *matCellDef="let report">{{ report.created_at | date:'short' }}</mat-cell>
        </ng-container>

        <!-- Actions Column -->
        <ng-container matColumnDef="actions">
          <mat-header-cell *matHeaderCellDef>Actions</mat-header-cell>
          <mat-cell *matCellDef="let report">
            <button mat-icon-button [routerLink]="['/reports', report.id]">
              <mat-icon>visibility</mat-icon>
            </button>
            <button mat-icon-button *ngIf="canValidate(report)" 
                    (click)="validateReport(report)" color="primary">
              <mat-icon>check</mat-icon>
            </button>
          </mat-cell>
        </ng-container>

        <mat-header-row *matHeaderRowDef="displayedColumns"></mat-header-row>
        <mat-row *matRowDef="let row; columns: displayedColumns;"></mat-row>
      </mat-table>
    </div>
  `,
  styles: [`
    .report-list {
      padding: 20px;
    }
    .header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 20px;
    }
    h1 {
      margin: 0;
    }
    mat-table {
      width: 100%;
    }
    .plagiat-low { color: #4caf50; font-weight: bold; }
    .plagiat-medium { color: #ff9800; font-weight: bold; }
    .plagiat-high { color: #f44336; font-weight: bold; }
  `]
})
export class ReportListComponent implements OnInit {
  reports: Report[] = [];
  displayedColumns = ['titre', 'type', 'auteur', 'statut', 'score', 'date', 'actions'];
  user: any;

  constructor(
    private reportService: ReportService,
    private authService: AuthService,
    private dialog: MatDialog,
    private snackBar: MatSnackBar
  ) {}

  ngOnInit(): void {
    this.authService.currentUser$.subscribe(user => {
      this.user = user;
      this.loadReports();
    });
  }

  loadReports(): void {
    this.reportService.getReports().subscribe({
      next: (reports) => {
        this.reports = reports;
      },
      error: () => {
        this.snackBar.open('Erreur lors du chargement des rapports', 'Fermer', { duration: 3000 });
      }
    });
  }

  getScoreClass(score: number): string {
    if (score < 15) return 'plagiat-low';
    if (score < 25) return 'plagiat-medium';
    return 'plagiat-high';
  }

  canValidate(report: Report): boolean {
    if (!this.user) return false;
    if (this.user.role === 'CHEF_DEPARTEMENT' && report.statut === 'SOUMIS') return true;
    if (this.user.role === 'DA' && report.statut === 'EN_REVUE_DA') return true;
    return false;
  }

  validateReport(report: Report): void {
    // Implémenter la logique de validation
  }
}

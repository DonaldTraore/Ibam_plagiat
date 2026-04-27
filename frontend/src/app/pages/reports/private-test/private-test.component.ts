import { Component } from '@angular/core';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';
import { Router } from '@angular/router';
import { MatSnackBar } from '@angular/material/snack-bar';
import { ReportService } from '../../../services/report.service';

@Component({
  selector: 'app-private-test',
  template: `
    <div class="private-test">
      <mat-card *ngIf="!testCompleted">
        <mat-card-header>
          <mat-card-title>
            <mat-icon>science</mat-icon>
            Test Privé de Plagiat
          </mat-card-title>
          <mat-card-subtitle>
            Téléchargez votre rapport pour vérifier le taux de plagiat avant soumission
          </mat-card-subtitle>
        </mat-card-header>

        <mat-card-content>
          <form [formGroup]="form" (ngSubmit)="onSubmit()">
            <mat-form-field appearance="outline" class="full-width">
              <mat-label>Titre du rapport</mat-label>
              <input matInput formControlName="titre" placeholder="Entrez le titre de votre rapport">
              <mat-error *ngIf="form.get('titre')?.hasError('required')">
                Le titre est requis
              </mat-error>
            </mat-form-field>

            <mat-form-field appearance="outline" class="full-width">
              <mat-label>Type de document</mat-label>
              <mat-select formControlName="type_document">
                <mat-option value="MEMOIRE">Mémoire de Licence</mat-option>
                <mat-option value="MASTER">Mémoire de Master</mat-option>
                <mat-option value="THESE">Thèse de Doctorat</mat-option>
                <mat-option value="DOCTORAT">Doctorat</mat-option>
              </mat-select>
            </mat-form-field>

            <div class="file-upload">
              <input type="file" #fileInput (change)="onFileSelected($event)" 
                     accept=".pdf,.docx,.doc,.txt" style="display: none">
              <button mat-stroked-button type="button" (click)="fileInput.click()" class="upload-btn">
                <mat-icon>upload_file</mat-icon>
                {{ selectedFile ? selectedFile.name : 'Choisir un fichier (PDF, DOCX, TXT)' }}
              </button>
              <mat-error *ngIf="!selectedFile && submitted">
                Un fichier est requis
              </mat-error>
            </div>

            <div class="info-box">
              <mat-icon>info</mat-icon>
              <p>Ce test est privé et ne sera pas visible par les validateurs. 
                 Vous pouvez vérifier votre taux de plagiat avant de soumettre officiellement.</p>
            </div>

            <div class="form-actions">
              <button mat-button type="button" routerLink="/dashboard">Annuler</button>
              <button mat-raised-button color="primary" type="submit" 
                      [disabled]="form.invalid || !selectedFile || loading">
                <mat-icon *ngIf="loading" class="spin">refresh</mat-icon>
                {{ loading ? 'Analyse en cours...' : 'Lancer le test' }}
              </button>
            </div>
          </form>
        </mat-card-content>
      </mat-card>

      <!-- RÉSULTATS DU TEST -->
      <mat-card *ngIf="testCompleted && testResult" class="result-card">
        <mat-card-header>
          <mat-card-title>
            <mat-icon [color]="getScoreColor()">assessment</mat-icon>
            Résultat du Test de Plagiat
          </mat-card-title>
        </mat-card-header>

        <mat-card-content>
          <div class="score-container" [class]="getScoreClass()">
            <div class="score-circle">
              <span class="score-value">{{ testResult.score_plagiat_global || 0 }}%</span>
              <span class="score-label">Taux de plagiat</span>
            </div>
          </div>

          <div class="result-message" [class]="getScoreClass()">
            <mat-icon>{{ getScoreIcon() }}</mat-icon>
            <p>{{ getScoreMessage() }}</p>
          </div>

          <mat-divider></mat-divider>

          <div class="action-buttons">
            <button mat-stroked-button color="warn" (click)="resubmit()">
              <mat-icon>refresh</mat-icon>
              Re-tester avec un autre fichier
            </button>
            <button mat-raised-button color="primary" (click)="proceedToSubmit()" 
                    *ngIf="canSubmit()">
              <mat-icon>send</mat-icon>
              Soumettre pour validation
            </button>
          </div>

          <div class="warning-box" *ngIf="!canSubmit()">
            <mat-icon>warning</mat-icon>
            <p><strong>Taux de plagiat trop élevé !</strong><br>
               Vous devez corriger votre rapport et re-tester. Le taux maximum accepté est de 25%.</p>
          </div>
        </mat-card-content>
      </mat-card>
    </div>
  `,
  styles: [`
    .private-test {
      padding: 20px;
      max-width: 600px;
      margin: 0 auto;
    }
    .full-width {
      width: 100%;
      margin-bottom: 15px;
    }
    .file-upload {
      margin: 20px 0;
    }
    .upload-btn {
      width: 100%;
      padding: 20px;
    }
    .info-box {
      background: #e3f2fd;
      padding: 15px;
      border-radius: 8px;
      margin: 20px 0;
      display: flex;
      gap: 10px;
      align-items: flex-start;
    }
    .info-box mat-icon {
      color: #1976d2;
    }
    .info-box p {
      margin: 0;
      font-size: 14px;
      color: #555;
    }
    .form-actions {
      display: flex;
      justify-content: flex-end;
      gap: 10px;
      margin-top: 20px;
    }
    .result-card {
      text-align: center;
    }
    .score-container {
      padding: 30px;
    }
    .score-circle {
      width: 150px;
      height: 150px;
      border-radius: 50%;
      border: 8px solid #ddd;
      display: flex;
      flex-direction: column;
      justify-content: center;
      align-items: center;
      margin: 0 auto;
    }
    .score-value {
      font-size: 36px;
      font-weight: bold;
    }
    .score-label {
      font-size: 12px;
      color: #666;
    }
    .low .score-circle {
      border-color: #4caf50;
    }
    .low .score-value {
      color: #4caf50;
    }
    .medium .score-circle {
      border-color: #ff9800;
    }
    .medium .score-value {
      color: #ff9800;
    }
    .high .score-circle {
      border-color: #f44336;
    }
    .high .score-value {
      color: #f44336;
    }
    .result-message {
      display: flex;
      align-items: center;
      justify-content: center;
      gap: 10px;
      padding: 15px;
      margin: 20px 0;
      border-radius: 8px;
    }
    .result-message.low {
      background: #e8f5e9;
      color: #2e7d32;
    }
    .result-message.medium {
      background: #fff3e0;
      color: #ef6c00;
    }
    .result-message.high {
      background: #ffebee;
      color: #c62828;
    }
    .action-buttons {
      display: flex;
      justify-content: center;
      gap: 15px;
      margin-top: 30px;
    }
    .warning-box {
      background: #ffebee;
      color: #c62828;
      padding: 15px;
      border-radius: 8px;
      margin-top: 20px;
      display: flex;
      gap: 10px;
      align-items: flex-start;
    }
    .spin {
      animation: spin 1s linear infinite;
    }
    @keyframes spin {
      from { transform: rotate(0deg); }
      to { transform: rotate(360deg); }
    }
    mat-card-title mat-icon {
      vertical-align: middle;
      margin-right: 8px;
    }
  `]
})
export class PrivateTestComponent {
  form: FormGroup;
  selectedFile: File | null = null;
  submitted = false;
  loading = false;
  testCompleted = false;
  testResult: any = null;
  createdReportId: number = 0;

  constructor(
    private fb: FormBuilder,
    private reportService: ReportService,
    private router: Router,
    private snackBar: MatSnackBar
  ) {
    this.form = this.fb.group({
      titre: ['', [Validators.required, Validators.maxLength(500)]],
      type_document: ['MEMOIRE', Validators.required]
    });
  }

  onFileSelected(event: any): void {
    const file = event.target.files[0];
    if (file) {
      const allowedTypes = [
        'application/pdf',
        'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        'application/msword',
        'text/plain'
      ];
      if (allowedTypes.includes(file.type) || 
          file.name.endsWith('.docx') || 
          file.name.endsWith('.doc') ||
          file.name.endsWith('.pdf') ||
          file.name.endsWith('.txt')) {
        this.selectedFile = file;
      } else {
        this.snackBar.open('Format de fichier non supporté. Utilisez PDF, DOCX ou TXT.', 'Fermer', { duration: 3000 });
      }
    }
  }

  onSubmit(): void {
    this.submitted = true;
    if (this.form.invalid || !this.selectedFile) return;

    this.loading = true;

    const formData = new FormData();
    formData.append('titre', this.form.value.titre);
    formData.append('type_document', this.form.value.type_document);
    formData.append('est_test_prive', 'true');
    formData.append('fichier', this.selectedFile);

    // 1. Créer le rapport en mode test privé
    this.reportService.createReport(formData).subscribe({
      next: (report) => {
        this.createdReportId = report.id;
        // 2. Lancer le test de plagiat
        this.runPlagiarismTest(report.id);
      },
      error: (err) => {
        this.loading = false;
        this.snackBar.open('Erreur lors du téléchargement', 'Fermer', { duration: 3000 });
      }
    });
  }

  runPlagiarismTest(reportId: number): void {
    this.reportService.testPlagiarism(reportId, 'PAR_CHAPITRE').subscribe({
      next: (result) => {
        this.loading = false;
        this.testCompleted = true;
        this.testResult = result;
        // Recharger le rapport pour avoir le score à jour
        this.reportService.getReport(reportId).subscribe(report => {
          this.testResult = report;
        });
      },
      error: () => {
        this.loading = false;
        this.snackBar.open('Erreur lors du test de plagiat', 'Fermer', { duration: 3000 });
      }
    });
  }

  getScoreClass(): string {
    const score = this.testResult?.score_plagiat_global || 0;
    if (score < 15) return 'low';
    if (score < 25) return 'medium';
    return 'high';
  }

  getScoreColor(): string {
    const score = this.testResult?.score_plagiat_global || 0;
    if (score < 15) return 'primary';
    if (score < 25) return 'accent';
    return 'warn';
  }

  getScoreIcon(): string {
    const score = this.testResult?.score_plagiat_global || 0;
    if (score < 15) return 'check_circle';
    if (score < 25) return 'warning';
    return 'error';
  }

  getScoreMessage(): string {
    const score = this.testResult?.score_plagiat_global || 0;
    if (score < 15) return 'Excellent ! Votre rapport a un faible taux de plagiat.';
    if (score < 25) return 'Attention ! Votre rapport présente un plagiat modéré.';
    return 'Plagiat élevé ! Vous devez corriger votre rapport.';
  }

  canSubmit(): boolean {
    const score = this.testResult?.score_plagiat_global || 0;
    return score < 25;
  }

  resubmit(): void {
    // Supprimer le test précédent et recommencer
    if (this.createdReportId) {
      this.reportService.deleteReport(this.createdReportId).subscribe(() => {
        this.resetForm();
      });
    } else {
      this.resetForm();
    }
  }

  resetForm(): void {
    this.testCompleted = false;
    this.testResult = null;
    this.createdReportId = 0;
    this.selectedFile = null;
    this.submitted = false;
    this.form.reset({ type_document: 'MEMOIRE' });
  }

  proceedToSubmit(): void {
    if (this.createdReportId) {
      // Soumettre le rapport pour validation
      this.reportService.submitReport(this.createdReportId).subscribe({
        next: () => {
          this.snackBar.open('Rapport soumis avec succès !', 'Fermer', { duration: 3000 });
          this.router.navigate(['/dashboard']);
        },
        error: () => {
          this.snackBar.open('Erreur lors de la soumission', 'Fermer', { duration: 3000 });
        }
      });
    }
  }
}

import { Component, OnInit } from '@angular/core';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';
import { Router, ActivatedRoute } from '@angular/router';
import { MatSnackBar } from '@angular/material/snack-bar';
import { ReportService } from '../../../services/report.service';

@Component({
  selector: 'app-report-form',
  template: `
    <div class="report-form">
      <mat-card>
        <mat-card-header>
          <mat-card-title>{{ isEdit ? 'Modifier' : 'Nouveau' }} Rapport</mat-card-title>
        </mat-card-header>

        <mat-card-content>
          <form [formGroup]="form" (ngSubmit)="onSubmit()">
            <mat-form-field appearance="outline" class="full-width">
              <mat-label>Titre du rapport</mat-label>
              <input matInput formControlName="titre" placeholder="Entrez le titre">
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

            <div class="file-upload" *ngIf="!isEdit">
              <input type="file" #fileInput (change)="onFileSelected($event)" 
                     accept=".pdf,.docx,.doc,.txt" style="display: none">
              <button mat-raised-button type="button" (click)="fileInput.click()">
                <mat-icon>upload</mat-icon>
                {{ selectedFile ? selectedFile.name : 'Choisir un fichier' }}
              </button>
              <mat-error *ngIf="!selectedFile && form.touched">
                Un fichier est requis
              </mat-error>
            </div>

            <mat-checkbox formControlName="est_test_prive">
              C'est un test privé (ne sera pas soumis pour validation)
            </mat-checkbox>

            <div class="form-actions">
              <button mat-button type="button" routerLink="/reports">Annuler</button>
              <button mat-raised-button color="primary" type="submit" 
                      [disabled]="form.invalid || (!selectedFile && !isEdit)">
                {{ isEdit ? 'Modifier' : 'Créer' }}
              </button>
            </div>
          </form>
        </mat-card-content>
      </mat-card>
    </div>
  `,
  styles: [`
    .report-form {
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
    mat-checkbox {
      margin: 15px 0;
      display: block;
    }
    .form-actions {
      display: flex;
      justify-content: flex-end;
      gap: 10px;
      margin-top: 20px;
    }
  `]
})
export class ReportFormComponent implements OnInit {
  form: FormGroup;
  isEdit = false;
  reportId: number = 0;
  selectedFile: File | null = null;

  constructor(
    private fb: FormBuilder,
    private reportService: ReportService,
    private router: Router,
    private route: ActivatedRoute,
    private snackBar: MatSnackBar
  ) {
    this.form = this.fb.group({
      titre: ['', [Validators.required, Validators.maxLength(500)]],
      type_document: ['MEMOIRE', Validators.required],
      est_test_prive: [false]
    });
  }

  ngOnInit(): void {
    const id = this.route.snapshot.paramMap.get('id');
    if (id) {
      this.isEdit = true;
      this.reportId = +id;
      this.loadReport();
    }
  }

  loadReport(): void {
    this.reportService.getReport(this.reportId).subscribe({
      next: (report) => {
        this.form.patchValue({
          titre: report.titre,
          type_document: report.type_document
        });
      }
    });
  }

  onFileSelected(event: any): void {
    const file = event.target.files[0];
    if (file) {
      const allowedTypes = ['application/pdf', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document', 'text/plain'];
      if (allowedTypes.includes(file.type) || file.name.endsWith('.docx') || file.name.endsWith('.doc')) {
        this.selectedFile = file;
      } else {
        this.snackBar.open('Format de fichier non supporté', 'Fermer', { duration: 3000 });
      }
    }
  }

  onSubmit(): void {
    if (this.form.invalid) return;

    const formData = new FormData();
    formData.append('titre', this.form.value.titre);
    formData.append('type_document', this.form.value.type_document);
    formData.append('est_test_prive', this.form.value.est_test_prive);

    if (this.selectedFile) {
      formData.append('fichier', this.selectedFile);
    }

    if (this.isEdit) {
      this.reportService.updateReport(this.reportId, this.form.value).subscribe({
        next: () => {
          this.snackBar.open('Rapport modifié avec succès !', 'Fermer', { duration: 3000 });
          this.router.navigate(['/reports']);
        },
        error: () => {
          this.snackBar.open('Erreur lors de la modification', 'Fermer', { duration: 3000 });
        }
      });
    } else {
      this.reportService.createReport(formData).subscribe({
        next: () => {
          this.snackBar.open('Rapport créé avec succès !', 'Fermer', { duration: 3000 });
          this.router.navigate(['/reports']);
        },
        error: () => {
          this.snackBar.open('Erreur lors de la création', 'Fermer', { duration: 3000 });
        }
      });
    }
  }
}

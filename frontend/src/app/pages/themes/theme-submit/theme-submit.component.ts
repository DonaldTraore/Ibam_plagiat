import { Component } from '@angular/core';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';
import { Router } from '@angular/router';
import { MatSnackBar } from '@angular/material/snack-bar';
import { HttpClient } from '@angular/common/http';
import { environment } from '../../../../environments/environment';

@Component({
  selector: 'app-theme-submit',
  template: `
    <div class="theme-submit">
      <mat-card *ngIf="!similarityChecked">
        <mat-card-header>
          <mat-card-title>
            <mat-icon>add_circle</mat-icon>
            Proposer un Thème
          </mat-card-title>
          <mat-card-subtitle>
            Soumettez votre proposition de thème de recherche
          </mat-card-subtitle>
        </mat-card-header>

        <mat-card-content>
          <form [formGroup]="form" (ngSubmit)="checkSimilarity()">
            <mat-form-field appearance="outline" class="full-width">
              <mat-label>Titre du thème</mat-label>
              <input matInput formControlName="titre" 
                     placeholder="Entrez le titre de votre thème de recherche">
              <mat-error *ngIf="form.get('titre')?.hasError('required')">
                Le titre est requis
              </mat-error>
              <mat-error *ngIf="form.get('titre')?.hasError('minlength')">
                Le titre doit contenir au moins 10 caractères
              </mat-error>
            </mat-form-field>

            <mat-form-field appearance="outline" class="full-width">
              <mat-label>Description</mat-label>
              <textarea matInput formControlName="description" rows="4"
                        placeholder="Décrivez brièvement votre thème de recherche">
              </textarea>
              <mat-error *ngIf="form.get('description')?.hasError('required')">
                La description est requise
              </mat-error>
            </mat-form-field>

            <mat-form-field appearance="outline" class="full-width">
              <mat-label>Département</mat-label>
              <mat-select formControlName="departement">
                <mat-option value="INFORMATIQUE">Informatique</mat-option>
                <mat-option value="MATHEMATIQUES">Mathématiques</mat-option>
                <mat-option value="PHYSIQUE">Physique</mat-option>
                <mat-option value="CHIMIE">Chimie</mat-option>
                <mat-option value="BIOLOGIE">Biologie</mat-option>
                <mat-option value="ECONOMIE">Économie</mat-option>
                <mat-option value="GESTION">Gestion</mat-option>
                <mat-option value="DROIT">Droit</mat-option>
                <mat-option value="MEDECINE">Médecine</mat-option>
                <mat-option value="AUTRE">Autre</mat-option>
              </mat-select>
            </mat-form-field>

            <div class="info-box">
              <mat-icon>info</mat-icon>
              <p>Avant de soumettre, nous vérifions si des thèmes similaires existent déjà dans la base de données.</p>
            </div>

            <div class="form-actions">
              <button mat-button type="button" routerLink="/dashboard">Annuler</button>
              <button mat-raised-button color="primary" type="submit" 
                      [disabled]="form.invalid || loading">
                <mat-icon *ngIf="loading" class="spin">refresh</mat-icon>
                {{ loading ? 'Vérification...' : 'Vérifier et Soumettre' }}
              </button>
            </div>
          </form>
        </mat-card-content>
      </mat-card>

      <!-- RÉSULTAT DE LA VÉRIFICATION -->
      <mat-card *ngIf="similarityChecked" class="result-card">
        <mat-card-header>
          <mat-card-title>
            <mat-icon [color]="hasSimilarThemes ? 'warn' : 'primary'">
              {{ hasSimilarThemes ? 'warning' : 'check_circle' }}
            </mat-icon>
            {{ hasSimilarThemes ? 'Thèmes similaires trouvés' : 'Aucun thème similaire' }}
          </mat-card-title>
        </mat-card-header>

        <mat-card-content>
          <div *ngIf="!hasSimilarThemes" class="success-message">
            <p>Aucun thème similaire n'a été trouvé dans la base de données.</p>
            <p>Votre proposition est originale et peut être soumise pour validation.</p>
          </div>

          <div *ngIf="hasSimilarThemes" class="warning-message">
            <p><strong>Attention !</strong> Des thèmes similaires existent déjà :</p>
            <mat-list>
              <mat-list-item *ngFor="let theme of similarThemes">
                <mat-icon mat-list-icon>topic</mat-icon>
                <div mat-line>{{ theme.titre }}</div>
                <div mat-line class="similarity-score">Similitude: {{ theme.similarity }}%</div>
              </mat-list-item>
            </mat-list>
            <p class="advice">Vous pouvez modifier votre titre pour plus d'originalité ou continuer si votre approche est différente.</p>
          </div>

          <mat-divider></mat-divider>

          <div class="action-buttons">
            <button mat-stroked-button (click)="modifyTheme()">
              <mat-icon>edit</mat-icon>
              Modifier mon thème
            </button>
            <button mat-raised-button color="primary" (click)="confirmSubmit()">
              <mat-icon>send</mat-icon>
              {{ hasSimilarThemes ? 'Soumettre quand même' : 'Soumettre le thème' }}
            </button>
          </div>
        </mat-card-content>
      </mat-card>
    </div>
  `,
  styles: [`
    .theme-submit {
      padding: 20px;
      max-width: 600px;
      margin: 0 auto;
    }
    .full-width {
      width: 100%;
      margin-bottom: 15px;
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
    .success-message {
      background: #e8f5e9;
      color: #2e7d32;
      padding: 20px;
      border-radius: 8px;
      margin: 20px 0;
    }
    .warning-message {
      background: #fff3e0;
      color: #ef6c00;
      padding: 20px;
      border-radius: 8px;
      margin: 20px 0;
      text-align: left;
    }
    .similarity-score {
      color: #f44336;
      font-size: 12px;
    }
    .advice {
      margin-top: 15px;
      font-style: italic;
    }
    .action-buttons {
      display: flex;
      justify-content: center;
      gap: 15px;
      margin-top: 30px;
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
export class ThemeSubmitComponent {
  form: FormGroup;
  loading = false;
  similarityChecked = false;
  hasSimilarThemes = false;
  similarThemes: any[] = [];

  private apiUrl = environment.apiUrl;

  constructor(
    private fb: FormBuilder,
    private http: HttpClient,
    private router: Router,
    private snackBar: MatSnackBar
  ) {
    this.form = this.fb.group({
      titre: ['', [Validators.required, Validators.minLength(10), Validators.maxLength(300)]],
      description: ['', [Validators.required, Validators.minLength(50)]],
      departement: ['INFORMATIQUE', Validators.required]
    });
  }

  checkSimilarity(): void {
    if (this.form.invalid) return;

    this.loading = true;

    // Appel API pour vérifier les thèmes similaires
    this.http.post(`${this.apiUrl}/themes/check-similarity/`, {
      titre: this.form.value.titre,
      description: this.form.value.description
    }).subscribe({
      next: (result: any) => {
        this.loading = false;
        this.similarityChecked = true;
        this.hasSimilarThemes = result.has_similar_themes;
        this.similarThemes = result.similar_themes || [];
      },
      error: () => {
        this.loading = false;
        // En cas d'erreur, on laisse passer quand même
        this.similarityChecked = true;
        this.hasSimilarThemes = false;
        this.snackBar.open('Impossible de vérifier les thèmes similaires. Vous pouvez continuer.', 'Fermer', { duration: 3000 });
      }
    });
  }

  modifyTheme(): void {
    this.similarityChecked = false;
    this.hasSimilarThemes = false;
    this.similarThemes = [];
  }

  confirmSubmit(): void {
    this.loading = true;

    this.http.post(`${this.apiUrl}/themes/`, this.form.value).subscribe({
      next: () => {
        this.loading = false;
        this.snackBar.open('Thème soumis avec succès !', 'Fermer', { duration: 3000 });
        this.router.navigate(['/themes']);
      },
      error: () => {
        this.loading = false;
        this.snackBar.open('Erreur lors de la soumission du thème', 'Fermer', { duration: 3000 });
      }
    });
  }
}

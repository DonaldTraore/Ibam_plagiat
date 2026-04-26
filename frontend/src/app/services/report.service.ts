import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../environments/environment';

export interface Report {
  id: number;
  titre: string;
  type_document: string;
  type_document_display: string;
  etudiant: any;
  fichier: string;
  fichier_nom_original: string;
  statut: string;
  statut_display: string;
  statut_color: string;
  score_plagiat_global: number;
  est_plagiat: boolean;
  date_soumission: string;
  created_at: string;
}

export interface ReportDetail extends Report {
  valide_par_chef: boolean;
  date_validation_chef: string;
  valide_par_da: boolean;
  date_validation_da: string;
  rejete_par: any;
  motif_rejet: string;
  date_rejet: string;
  pdf_signe: string;
  departement: string;
  nombre_pages: number;
  nombre_mots: number;
  chapters: any[];
  plagiarism_results: any[];
}

@Injectable({
  providedIn: 'root'
})
export class ReportService {
  private apiUrl = environment.apiUrl;

  constructor(private http: HttpClient) { }

  getReports(): Observable<Report[]> {
    return this.http.get<Report[]>(`${this.apiUrl}/reports/`);
  }

  getMyReports(): Observable<Report[]> {
    return this.http.get<Report[]>(`${this.apiUrl}/reports/my-reports/`);
  }

  getMyTests(): Observable<Report[]> {
    return this.http.get<Report[]>(`${this.apiUrl}/reports/my-tests/`);
  }

  getReport(id: number): Observable<ReportDetail> {
    return this.http.get<ReportDetail>(`${this.apiUrl}/reports/${id}/`);
  }

  createReport(formData: FormData): Observable<Report> {
    return this.http.post<Report>(`${this.apiUrl}/reports/create/`, formData);
  }

  updateReport(id: number, data: any): Observable<Report> {
    return this.http.put<Report>(`${this.apiUrl}/reports/${id}/update/`, data);
  }

  deleteReport(id: number): Observable<any> {
    return this.http.delete(`${this.apiUrl}/reports/${id}/delete/`);
  }

  submitReport(id: number): Observable<any> {
    return this.http.post(`${this.apiUrl}/reports/${id}/submit/`, { confirmation: true });
  }

  validateReport(id: number, action: 'valider' | 'rejeter', motif?: string): Observable<any> {
    return this.http.post(`${this.apiUrl}/reports/${id}/validate/`, { action, motif_rejet: motif });
  }

  testPlagiarism(id: number, typeDetection: string = 'PAR_CHAPITRE'): Observable<any> {
    return this.http.post(`${this.apiUrl}/reports/${id}/test-plagiarism/`, { type_detection: typeDetection });
  }

  getStatistics(): Observable<any> {
    return this.http.get(`${this.apiUrl}/reports/statistics/`);
  }
}

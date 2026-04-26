import { Injectable } from '@angular/core';
import {
  HttpRequest,
  HttpHandler,
  HttpEvent,
  HttpInterceptor,
  HttpErrorResponse
} from '@angular/common/http';
import { Observable, throwError } from 'rxjs';
import { catchError } from 'rxjs/operators';
import { MatSnackBar } from '@angular/material/snack-bar';

@Injectable()
export class ErrorInterceptor implements HttpInterceptor {

  constructor(private snackBar: MatSnackBar) {}

  intercept(request: HttpRequest<unknown>, next: HttpHandler): Observable<HttpEvent<unknown>> {
    return next.handle(request).pipe(
      catchError((error: HttpErrorResponse) => {
        let errorMessage = 'Une erreur est survenue';

        if (error.error instanceof ErrorEvent) {
          // Erreur client
          errorMessage = error.error.message;
        } else {
          // Erreur serveur
          if (error.status === 400) {
            errorMessage = 'Requête invalide';
            if (error.error && typeof error.error === 'object') {
              const errors = Object.values(error.error).flat();
              if (errors.length > 0) {
                errorMessage = errors.join(', ');
              }
            }
          } else if (error.status === 403) {
            errorMessage = 'Accès refusé';
          } else if (error.status === 404) {
            errorMessage = 'Ressource non trouvée';
          } else if (error.status === 500) {
            errorMessage = 'Erreur serveur';
          }
        }

        this.snackBar.open(errorMessage, 'Fermer', {
          duration: 5000,
          panelClass: 'error-snackbar'
        });

        return throwError(() => error);
      })
    );
  }
}

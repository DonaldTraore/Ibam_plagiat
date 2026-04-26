import { Component } from '@angular/core';

@Component({
  selector: 'app-confirm-dialog',
  template: `
    <div class="confirm-dialog">
      <h3>Confirmation</h3>
      <p>Êtes-vous sûr de vouloir effectuer cette action ?</p>
    </div>
  `,
  styles: ['.confirm-dialog { padding: 20px; }']
})
export class ConfirmDialogComponent {}

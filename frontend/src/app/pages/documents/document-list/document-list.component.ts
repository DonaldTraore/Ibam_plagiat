import { Component } from '@angular/core';

@Component({
  selector: 'app-document-list',
  template: `
    <div class="document-list">
      <h2>Documents de Référence</h2>
      <p>La liste des documents de référence sera affichée ici.</p>
    </div>
  `,
  styles: ['.document-list { padding: 20px; }']
})
export class DocumentListComponent {}

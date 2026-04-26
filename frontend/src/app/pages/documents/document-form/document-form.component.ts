import { Component } from '@angular/core';

@Component({
  selector: 'app-document-form',
  template: `
    <div class="document-form">
      <h2>Ajouter un Document</h2>
      <p>Le formulaire d'ajout de document sera affiché ici.</p>
    </div>
  `,
  styles: ['.document-form { padding: 20px; }']
})
export class DocumentFormComponent {}

import { Component } from '@angular/core';

@Component({
  selector: 'app-theme-list',
  template: `
    <div class="theme-list">
      <h2>Liste des Thèmes</h2>
      <p>Les thèmes de recherche seront affichés ici.</p>
    </div>
  `,
  styles: ['.theme-list { padding: 20px; }']
})
export class ThemeListComponent {}

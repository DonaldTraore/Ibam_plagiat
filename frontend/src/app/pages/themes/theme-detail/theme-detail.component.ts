import { Component } from '@angular/core';

@Component({
  selector: 'app-theme-detail',
  template: `
    <div class="theme-detail">
      <h2>Détail du Thème</h2>
      <p>Les détails du thème seront affichés ici.</p>
    </div>
  `,
  styles: ['.theme-detail { padding: 20px; }']
})
export class ThemeDetailComponent {}

import { Component } from '@angular/core';

@Component({
  selector: 'app-theme-form',
  template: `
    <div class="theme-form">
      <h2>Formulaire Thème</h2>
      <p>Le formulaire de création/modification de thème sera affiché ici.</p>
    </div>
  `,
  styles: ['.theme-form { padding: 20px; }']
})
export class ThemeFormComponent {}

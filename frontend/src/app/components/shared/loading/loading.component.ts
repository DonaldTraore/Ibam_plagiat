import { Component } from '@angular/core';

@Component({
  selector: 'app-loading',
  template: `
    <div class="loading">
      <p>Chargement...</p>
    </div>
  `,
  styles: ['.loading { padding: 20px; text-align: center; }']
})
export class LoadingComponent {}

import { Component } from '@angular/core';

@Component({
  selector: 'app-history-list',
  template: `
    <div class="history-list">
      <h2>Historique</h2>
      <p>L'historique de vos activités sera affiché ici.</p>
    </div>
  `,
  styles: ['.history-list { padding: 20px; }']
})
export class HistoryListComponent {}

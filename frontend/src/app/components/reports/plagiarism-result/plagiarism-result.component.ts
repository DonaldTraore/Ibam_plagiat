import { Component } from '@angular/core';

@Component({
  selector: 'app-plagiarism-result',
  template: `
    <div class="plagiarism-result">
      <h3>Résultat du Test de Plagiat</h3>
      <p>Les résultats du test de plagiat seront affichés ici.</p>
    </div>
  `,
  styles: ['.plagiarism-result { padding: 15px; }']
})
export class PlagiarismResultComponent {}

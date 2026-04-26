import { Component } from '@angular/core';

@Component({
  selector: 'app-footer',
  template: `
    <footer class="footer">
      <div class="footer-content">
        <p>&copy; 2024 Système de Détection de Plagiat - IBAM</p>
        <p class="footer-links">
          <a href="#">Aide</a> | 
          <a href="#">Contact</a> | 
          <a href="#">Confidentialité</a>
        </p>
      </div>
    </footer>
  `,
  styles: [`
    .footer {
      background: #f5f5f5;
      padding: 15px;
      text-align: center;
      font-size: 12px;
      color: #666;
      border-top: 1px solid #e0e0e0;
    }
    .footer-content p {
      margin: 5px 0;
    }
    .footer-links a {
      color: #666;
      text-decoration: none;
    }
    .footer-links a:hover {
      color: #3f51b5;
    }
  `]
})
export class FooterComponent {}

import { Component } from '@angular/core';

@Component({
  selector: 'app-notification-list',
  template: `
    <div class="notification-list">
      <h2>Notifications</h2>
      <p>Vos notifications seront affichées ici.</p>
    </div>
  `,
  styles: ['.notification-list { padding: 20px; }']
})
export class NotificationListComponent {}

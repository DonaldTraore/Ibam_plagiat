import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { AuthGuard } from './guards/auth.guard';
import { RoleGuard } from './guards/role.guard';

// Components
import { LoginComponent } from './pages/auth/login/login.component';
import { DashboardComponent } from './pages/dashboard/dashboard.component';
import { ReportListComponent } from './pages/reports/report-list/report-list.component';
import { ReportDetailComponent } from './pages/reports/report-detail/report-detail.component';
import { ReportFormComponent } from './pages/reports/report-form/report-form.component';
import { ThemeListComponent } from './pages/themes/theme-list/theme-list.component';
import { ThemeDetailComponent } from './pages/themes/theme-detail/theme-detail.component';
import { ThemeFormComponent } from './pages/themes/theme-form/theme-form.component';
import { NotificationListComponent } from './pages/notifications/notification-list/notification-list.component';
import { HistoryListComponent } from './pages/history/history-list/history-list.component';
import { DocumentListComponent } from './pages/documents/document-list/document-list.component';
import { DocumentFormComponent } from './pages/documents/document-form/document-form.component';

const routes: Routes = [
  { path: '', redirectTo: '/login', pathMatch: 'full' },
  { path: 'login', component: LoginComponent },
  {
    path: 'dashboard',
    component: DashboardComponent,
    canActivate: [AuthGuard]
  },
  // Reports - Workflow Étudiant
  {
    path: 'reports',
    component: ReportListComponent,
    canActivate: [AuthGuard]
  },
  {
    path: 'reports/create',
    component: ReportFormComponent,
    canActivate: [AuthGuard, RoleGuard],
    data: { roles: ['ETUDIANT'] }
  },
  {
    path: 'reports/private-test',
    component: ReportFormComponent,
    canActivate: [AuthGuard, RoleGuard],
    data: { roles: ['ETUDIANT'] }
  },
  {
    path: 'reports/my-submissions',
    component: ReportListComponent,
    canActivate: [AuthGuard, RoleGuard],
    data: { roles: ['ETUDIANT'] }
  },
  {
    path: 'reports/pending',
    component: ReportListComponent,
    canActivate: [AuthGuard, RoleGuard],
    data: { roles: ['CHEF_DEPARTEMENT'] }
  },
  {
    path: 'reports/final-validation',
    component: ReportListComponent,
    canActivate: [AuthGuard, RoleGuard],
    data: { roles: ['DA'] }
  },
  {
    path: 'reports/:id',
    component: ReportDetailComponent,
    canActivate: [AuthGuard]
  },
  {
    path: 'reports/:id/edit',
    component: ReportFormComponent,
    canActivate: [AuthGuard, RoleGuard],
    data: { roles: ['ETUDIANT'] }
  },
  // Themes - Workflow
  {
    path: 'themes',
    component: ThemeListComponent,
    canActivate: [AuthGuard]
  },
  {
    path: 'themes/create',
    component: ThemeFormComponent,
    canActivate: [AuthGuard, RoleGuard],
    data: { roles: ['ETUDIANT'] }
  },
  {
    path: 'themes/submit',
    component: ThemeFormComponent,
    canActivate: [AuthGuard, RoleGuard],
    data: { roles: ['ETUDIANT'] }
  },
  {
    path: 'themes/pending',
    component: ThemeListComponent,
    canActivate: [AuthGuard, RoleGuard],
    data: { roles: ['CHEF_DEPARTEMENT'] }
  },
  {
    path: 'themes/final-validation',
    component: ThemeListComponent,
    canActivate: [AuthGuard, RoleGuard],
    data: { roles: ['DA'] }
  },
  {
    path: 'themes/:id',
    component: ThemeDetailComponent,
    canActivate: [AuthGuard]
  },
  {
    path: 'themes/:id/edit',
    component: ThemeFormComponent,
    canActivate: [AuthGuard, RoleGuard],
    data: { roles: ['ETUDIANT'] }
  },
  // Documents - Secrétaire
  {
    path: 'documents',
    component: DocumentListComponent,
    canActivate: [AuthGuard]
  },
  {
    path: 'documents/upload',
    component: DocumentFormComponent,
    canActivate: [AuthGuard, RoleGuard],
    data: { roles: ['SECRETAIRE'] }
  },
  {
    path: 'documents/create',
    component: DocumentFormComponent,
    canActivate: [AuthGuard, RoleGuard],
    data: { roles: ['SECRETAIRE', 'CHEF_DEPARTEMENT', 'DA'] }
  },
  // Notifications
  {
    path: 'notifications',
    component: NotificationListComponent,
    canActivate: [AuthGuard]
  },
  // History
  {
    path: 'history',
    component: HistoryListComponent,
    canActivate: [AuthGuard]
  },
  { path: '**', redirectTo: '/login' }
];

@NgModule({
  imports: [RouterModule.forRoot(routes)],
  exports: [RouterModule]
})
export class AppRoutingModule { }

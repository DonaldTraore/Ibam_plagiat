from django.urls import path
from . import views

urlpatterns = [
    # Liste et création
    path('', views.ReportListView.as_view(), name='report-list'),
    path('create/', views.ReportCreateView.as_view(), name='report-create'),
    
    # Détail, mise à jour, suppression
    path('<int:pk>/', views.ReportDetailView.as_view(), name='report-detail'),
    path('<int:pk>/update/', views.ReportUpdateView.as_view(), name='report-update'),
    path('<int:pk>/delete/', views.ReportDeleteView.as_view(), name='report-delete'),
    
    # Actions sur les rapports
    path('<int:pk>/submit/', views.ReportSubmitView.as_view(), name='report-submit'),
    path('<int:pk>/validate/', views.ReportValidateView.as_view(), name='report-validate'),
    path('<int:pk>/test-plagiarism/', views.ReportTestPlagiarismView.as_view(), name='report-test-plagiarism'),
    
    # Rapports de l'étudiant
    path('my-reports/', views.EtudiantReportListView.as_view(), name='my-reports'),
    path('my-tests/', views.EtudiantTestPrivateListView.as_view(), name='my-private-tests'),
    
    # Résultats de plagiat
    path('plagiarism-results/<int:pk>/', views.PlagiarismResultDetailView.as_view(), name='plagiarism-result-detail'),
    
    # Statistiques
    path('statistics/', views.ReportStatisticsView.as_view(), name='report-statistics'),
]

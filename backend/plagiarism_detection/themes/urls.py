from django.urls import path
from . import views

urlpatterns = [
    # Liste et création
    path('', views.ThemeListView.as_view(), name='theme-list'),
    path('create/', views.ThemeCreateView.as_view(), name='theme-create'),
    
    # Vérification similarité avant création
    path('check-similarity/', views.ThemeCheckSimilarityView.as_view(), name='theme-check-similarity'),
    
    # Détail, mise à jour, suppression
    path('<int:pk>/', views.ThemeDetailView.as_view(), name='theme-detail'),
    path('<int:pk>/update/', views.ThemeUpdateView.as_view(), name='theme-update'),
    path('<int:pk>/delete/', views.ThemeDeleteView.as_view(), name='theme-delete'),
    
    # Actions sur les thèmes
    path('<int:pk>/submit/', views.ThemeSubmitView.as_view(), name='theme-submit'),
    path('<int:pk>/validate/', views.ThemeValidateView.as_view(), name='theme-validate'),
    path('<int:pk>/test-similarity/', views.ThemeTestSimilarityView.as_view(), name='theme-test-similarity'),
    
    # Thèmes de l'étudiant
    path('my-themes/', views.EtudiantThemeListView.as_view(), name='my-themes'),
    path('my-tests/', views.EtudiantThemeTestListView.as_view(), name='my-private-theme-tests'),
    
    # Statistiques
    path('statistics/', views.ThemeStatisticsView.as_view(), name='theme-statistics'),
]

from django.urls import path
from . import views

urlpatterns = [
    # Gestion des utilisateurs
    path('users/', views.UserListView.as_view(), name='user-list'),
    path('users/create/', views.UserCreateView.as_view(), name='user-create'),
    path('users/<int:pk>/', views.UserDetailView.as_view(), name='user-detail'),
    path('users/<int:pk>/update/', views.UserUpdateView.as_view(), name='user-update'),
    path('users/<int:pk>/delete/', views.UserDeleteView.as_view(), name='user-delete'),
    
    # Utilisateur connecté
    path('me/', views.CurrentUserView.as_view(), name='current-user'),
    path('me/change-password/', views.ChangePasswordView.as_view(), name='change-password'),
    path('me/profile/', views.UserProfileUpdateView.as_view(), name='user-profile-update'),
    
    # Listes par rôle
    path('etudiants/', views.EtudiantListView.as_view(), name='etudiant-list'),
    path('chefs-departement/', views.ChefDepartementListView.as_view(), name='chef-departement-list'),
    path('da/', views.DAListView.as_view(), name='da-list'),
    path('secretaires/', views.SecretaireListView.as_view(), name='secretaire-list'),
]

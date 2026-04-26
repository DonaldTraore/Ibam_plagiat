from django.urls import path
from . import views

urlpatterns = [
    path('', views.ReferenceDocumentListView.as_view(), name='reference-document-list'),
    path('create/', views.ReferenceDocumentCreateView.as_view(), name='reference-document-create'),
    path('<int:pk>/', views.ReferenceDocumentDetailView.as_view(), name='reference-document-detail'),
    path('<int:pk>/update/', views.ReferenceDocumentUpdateView.as_view(), name='reference-document-update'),
    path('<int:pk>/delete/', views.ReferenceDocumentDeleteView.as_view(), name='reference-document-delete'),
    path('statistics/', views.ReferenceDocumentStatisticsView.as_view(), name='reference-document-statistics'),
]

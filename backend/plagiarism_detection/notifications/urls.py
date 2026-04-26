from django.urls import path
from . import views

urlpatterns = [
    path('', views.NotificationListView.as_view(), name='notification-list'),
    path('unread/', views.NotificationUnreadListView.as_view(), name='notification-unread-list'),
    path('<int:pk>/', views.NotificationDetailView.as_view(), name='notification-detail'),
    path('<int:pk>/mark-as-read/', views.NotificationMarkAsReadView.as_view(), name='notification-mark-read'),
    path('mark-all-as-read/', views.NotificationMarkAllAsReadView.as_view(), name='notification-mark-all-read'),
    path('<int:pk>/delete/', views.NotificationDeleteView.as_view(), name='notification-delete'),
    path('count/', views.NotificationCountView.as_view(), name='notification-count'),
]

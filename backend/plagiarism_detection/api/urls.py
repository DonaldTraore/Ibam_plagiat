from django.urls import path
from . import views

urlpatterns = [
    # Dashboard
    path('dashboard/', views.DashboardView.as_view(), name='dashboard'),
    path('dashboard/stats/', views.DashboardStatsView.as_view(), name='dashboard-stats'),
    
    # Search
    path('search/', views.GlobalSearchView.as_view(), name='global-search'),
    
    # System status
    path('status/', views.SystemStatusView.as_view(), name='system-status'),
]

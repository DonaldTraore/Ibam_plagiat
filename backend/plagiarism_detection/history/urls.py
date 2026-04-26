from django.urls import path
from . import views

urlpatterns = [
    path('', views.HistoryListView.as_view(), name='history-list'),
    path('my-history/', views.UserHistoryView.as_view(), name='my-history'),
]

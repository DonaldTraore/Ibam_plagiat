from rest_framework import generics, permissions, filters
from django_filters.rest_framework import DjangoFilterBackend
from .models import History
from .serializers import HistorySerializer


class HistoryListView(generics.ListAPIView):
    """
    Liste l'historique avec filtrage.
    """
    queryset = History.objects.all()
    serializer_class = HistorySerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['action', 'entity_type', 'departement']
    search_fields = ['details', 'user__first_name', 'user__last_name', 'user__email']
    ordering_fields = ['created_at']
    ordering = ['-created_at']
    
    def get_queryset(self):
        user = self.request.user
        queryset = History.objects.all()
        
        # Filtrer selon le rôle
        if user.is_etudiant:
            # Étudiant: ne voit que son propre historique
            queryset = queryset.filter(user=user)
        elif user.is_chef_departement:
            # Chef de département: voit l'historique de son département
            queryset = queryset.filter(departement=user.departement)
        
        return queryset.select_related('user')


class UserHistoryView(generics.ListAPIView):
    """
    Liste l'historique de l'utilisateur connecté.
    """
    serializer_class = HistorySerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return History.objects.filter(user=self.request.user).select_related('user')

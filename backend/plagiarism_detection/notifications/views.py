from rest_framework import generics, status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from django.utils import timezone
from .models import Notification
from .serializers import NotificationSerializer, NotificationListSerializer
from ..utils.email_sender import send_notification_email


class NotificationListView(generics.ListAPIView):
    """
    Liste les notifications de l'utilisateur connecté.
    """
    serializer_class = NotificationListSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user).select_related('user')


class NotificationUnreadListView(generics.ListAPIView):
    """
    Liste les notifications non lues de l'utilisateur connecté.
    """
    serializer_class = NotificationListSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user, lu=False).select_related('user')


class NotificationDetailView(generics.RetrieveAPIView):
    """
    Détail d'une notification.
    """
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user).select_related('user')
    
    def get(self, request, *args, **kwargs):
        notification = self.get_object()
        
        # Marquer comme lue si pas déjà lu
        if not notification.lu:
            notification.marquer_comme_lu()
        
        serializer = self.get_serializer(notification)
        return Response(serializer.data)


class NotificationMarkAsReadView(APIView):
    """
    Marquer une notification comme lue.
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request, pk):
        notification = get_object_or_404(Notification, pk=pk, user=request.user)
        notification.marquer_comme_lu()
        return Response({"message": "Notification marquée comme lue."}, status=status.HTTP_200_OK)


class NotificationMarkAllAsReadView(APIView):
    """
    Marquer toutes les notifications comme lues.
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        Notification.objects.filter(user=request.user, lu=False).update(
            lu=True,
            date_lecture=timezone.now()
        )
        return Response({"message": "Toutes les notifications marquées comme lues."}, status=status.HTTP_200_OK)


class NotificationDeleteView(generics.DestroyAPIView):
    """
    Supprimer une notification.
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user)


class NotificationCountView(APIView):
    """
    Retourne le nombre de notifications non lues.
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        count = Notification.objects.filter(user=request.user, lu=False).count()
        return Response({"unread_count": count})

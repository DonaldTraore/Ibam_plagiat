from rest_framework import serializers
from .models import Notification
from plagiarism_detection.accounts.serializers import UserSerializer


class NotificationSerializer(serializers.ModelSerializer):
    """
    Sérialiseur pour les notifications.
    """
    user = UserSerializer(read_only=True)
    type_display = serializers.CharField(source='get_type_display', read_only=True)
    
    class Meta:
        model = Notification
        fields = [
            'id', 'user', 'type', 'type_display', 'titre', 'message',
            'lien', 'lu', 'date_lecture', 'email_envoye', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class NotificationListSerializer(serializers.ModelSerializer):
    """
    Sérialiseur allégé pour la liste des notifications.
    """
    type_display = serializers.CharField(source='get_type_display', read_only=True)
    
    class Meta:
        model = Notification
        fields = ['id', 'type', 'type_display', 'titre', 'message', 'lu', 'created_at']

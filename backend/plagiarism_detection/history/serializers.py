from rest_framework import serializers
from .models import History
from plagiarism_detection.accounts.serializers import UserSerializer


class HistorySerializer(serializers.ModelSerializer):
    """
    Sérialiseur pour l'historique.
    """
    user = UserSerializer(read_only=True)
    action_display = serializers.CharField(source='get_action_display', read_only=True)
    entity_type_display = serializers.CharField(source='get_entity_type_display', read_only=True)
    
    class Meta:
        model = History
        fields = [
            'id', 'user', 'action', 'action_display', 'entity_type', 'entity_type_display',
            'entity_id', 'details', 'ip_address', 'departement', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class HistoryCreateSerializer(serializers.ModelSerializer):
    """
    Sérialiseur pour créer une entrée d'historique.
    """
    class Meta:
        model = History
        fields = [
            'action', 'entity_type', 'entity_id', 'details', 'departement'
        ]

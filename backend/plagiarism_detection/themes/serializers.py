from rest_framework import serializers
from .models import Theme
from plagiarism_detection.accounts.serializers import UserSerializer


class ThemeListSerializer(serializers.ModelSerializer):
    """
    Sérialiseur pour la liste des thèmes.
    """
    etudiant = UserSerializer(read_only=True)
    statut_display = serializers.CharField(source='get_statut_display', read_only=True)
    statut_color = serializers.CharField(source='get_statut_display_color', read_only=True)
    
    class Meta:
        model = Theme
        fields = [
            'id', 'titre', 'etudiant', 'statut', 'statut_display', 'statut_color',
            'score_similarite', 'date_soumission', 'created_at'
        ]


class ThemeDetailSerializer(serializers.ModelSerializer):
    """
    Sérialiseur pour le détail d'un thème.
    """
    etudiant = UserSerializer(read_only=True)
    rejete_par = UserSerializer(read_only=True)
    statut_display = serializers.CharField(source='get_statut_display', read_only=True)
    statut_color = serializers.CharField(source='get_statut_display_color', read_only=True)
    
    class Meta:
        model = Theme
        fields = [
            'id', 'titre', 'description', 'mots_cles', 'etudiant', 'fichier',
            'statut', 'statut_display', 'statut_color',
            'valide_par_chef', 'date_validation_chef',
            'valide_par_da', 'date_validation_da',
            'rejete_par', 'motif_rejet', 'date_rejet',
            'departement', 'est_test_prive',
            'score_similarite', 'themes_similaires',
            'date_soumission', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'etudiant', 'departement', 'score_similarite', 'created_at', 'updated_at']


class ThemeCreateSerializer(serializers.ModelSerializer):
    """
    Sérialiseur pour la création d'un thème.
    """
    fichier = serializers.FileField(required=False)
    departement = serializers.CharField(required=False, write_only=True)
    
    class Meta:
        model = Theme
        fields = ['id', 'titre', 'description', 'mots_cles', 'fichier', 'est_test_prive', 'departement']
        read_only_fields = ['id']
    
    def validate_fichier(self, value):
        """Valide le format du fichier."""
        if value:
            import os
            ext = os.path.splitext(value.name)[1].lower()
            allowed_extensions = ['.pdf', '.docx', '.doc', '.txt']
            
            if ext not in allowed_extensions:
                raise serializers.ValidationError(
                    f"Format de fichier non supporté. Formats acceptés: {', '.join(allowed_extensions)}"
                )
            
            if value.size > 10 * 1024 * 1024:
                raise serializers.ValidationError("Le fichier ne doit pas dépasser 10MB.")
        
        return value


class ThemeUpdateSerializer(serializers.ModelSerializer):
    """
    Sérialiseur pour la mise à jour d'un thème.
    """
    class Meta:
        model = Theme
        fields = ['titre', 'description', 'mots_cles']


class ThemeValidationSerializer(serializers.Serializer):
    """
    Sérialiseur pour la validation d'un thème.
    """
    action = serializers.ChoiceField(choices=['valider', 'rejeter'])
    motif_rejet = serializers.CharField(required=False, allow_blank=True)
    
    def validate(self, attrs):
        if attrs['action'] == 'rejeter' and not attrs.get('motif_rejet'):
            raise serializers.ValidationError(
                {"motif_rejet": "Le motif de rejet est obligatoire."}
            )
        return attrs


class ThemeTestSimilaritySerializer(serializers.Serializer):
    """
    Sérialiseur pour tester la similarité d'un thème.
    """
    confirmation = serializers.BooleanField(required=True)


class ThemeSubmitSerializer(serializers.Serializer):
    """
    Sérialiseur pour soumettre un thème.
    """
    confirmation = serializers.BooleanField(required=True)

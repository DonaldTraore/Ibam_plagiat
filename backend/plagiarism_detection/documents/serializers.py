from rest_framework import serializers
from .models import ReferenceDocument
from plagiarism_detection.accounts.serializers import UserSerializer


class ReferenceDocumentListSerializer(serializers.ModelSerializer):
    """
    Sérialiseur pour la liste des documents de référence.
    """
    ajoute_par = UserSerializer(read_only=True)
    type_document_display = serializers.CharField(source='get_type_document_display', read_only=True)
    
    class Meta:
        model = ReferenceDocument
        fields = [
            'id', 'titre', 'auteur', 'annee', 'type_document', 'type_document_display',
            'departement', 'nombre_pages', 'nombre_mots', 'est_actif', 'date_ajout'
        ]


class ReferenceDocumentDetailSerializer(serializers.ModelSerializer):
    """
    Sérialiseur pour le détail d'un document de référence.
    """
    ajoute_par = UserSerializer(read_only=True)
    type_document_display = serializers.CharField(source='get_type_document_display', read_only=True)
    
    class Meta:
        model = ReferenceDocument
        fields = [
            'id', 'titre', 'auteur', 'annee', 'description', 'fichier', 'fichier_nom_original',
            'type_document', 'type_document_display', 'departement', 'mots_cles',
            'nombre_pages', 'nombre_mots', 'contenu_extrait', 'ajoute_par',
            'est_actif', 'date_ajout', 'updated_at'
        ]
        read_only_fields = ['id', 'ajoute_par', 'nombre_pages', 'nombre_mots', 'contenu_extrait', 'date_ajout', 'updated_at']


class ReferenceDocumentCreateSerializer(serializers.ModelSerializer):
    """
    Sérialiseur pour la création d'un document de référence.
    """
    fichier = serializers.FileField(required=True)
    
    class Meta:
        model = ReferenceDocument
        fields = [
            'id', 'titre', 'auteur', 'annee', 'description', 'fichier',
            'type_document', 'departement', 'mots_cles'
        ]
        read_only_fields = ['id']
    
    def validate_fichier(self, value):
        """Valide le format du fichier."""
        import os
        ext = os.path.splitext(value.name)[1].lower()
        allowed_extensions = ['.pdf', '.docx', '.doc', '.txt']
        
        if ext not in allowed_extensions:
            raise serializers.ValidationError(
                f"Format de fichier non supporté. Formats acceptés: {', '.join(allowed_extensions)}"
            )
        
        if value.size > 50 * 1024 * 1024:  # 50MB pour les documents de référence
            raise serializers.ValidationError("Le fichier ne doit pas dépasser 50MB.")
        
        return value


class ReferenceDocumentUpdateSerializer(serializers.ModelSerializer):
    """
    Sérialiseur pour la mise à jour d'un document de référence.
    """
    class Meta:
        model = ReferenceDocument
        fields = [
            'titre', 'auteur', 'annee', 'description',
            'type_document', 'departement', 'mots_cles', 'est_actif'
        ]

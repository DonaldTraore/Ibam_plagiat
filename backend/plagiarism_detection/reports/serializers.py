from rest_framework import serializers
from .models import Report, ReportChapter, PlagiarismResult
from plagiarism_detection.accounts.serializers import UserSerializer


class ReportChapterSerializer(serializers.ModelSerializer):
    """
    Sérialiseur pour les chapitres de rapport.
    """
    class Meta:
        model = ReportChapter
        fields = [
            'id', 'report', 'numero_chapitre', 'titre_chapitre',
            'contenu', 'nombre_mots', 'score_plagiat', 'passages_plagies',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class PlagiarismResultSerializer(serializers.ModelSerializer):
    """
    Sérialiseur pour les résultats de plagiat.
    """
    teste_par = UserSerializer(read_only=True)
    depasse_seuil = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = PlagiarismResult
        fields = [
            'id', 'report', 'type_detection', 'score_global',
            'score_par_chapitre', 'similitudes_trouvees',
            'teste_par', 'date_test', 'est_valide', 'depasse_seuil',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class ReportListSerializer(serializers.ModelSerializer):
    """
    Sérialiseur pour la liste des rapports (version allégée).
    """
    etudiant = UserSerializer(read_only=True)
    type_document_display = serializers.CharField(source='get_type_document_display', read_only=True)
    statut_display = serializers.CharField(source='get_statut_display', read_only=True)
    statut_color = serializers.CharField(source='get_statut_display_color', read_only=True)
    
    class Meta:
        model = Report
        fields = [
            'id', 'titre', 'type_document', 'type_document_display',
            'etudiant', 'statut', 'statut_display', 'statut_color',
            'score_plagiat_global', 'est_plagiat', 'date_soumission',
            'created_at'
        ]


class ReportDetailSerializer(serializers.ModelSerializer):
    """
    Sérialiseur pour le détail d'un rapport.
    """
    etudiant = UserSerializer(read_only=True)
    rejete_par = UserSerializer(read_only=True)
    chapters = ReportChapterSerializer(many=True, read_only=True)
    plagiarism_results = PlagiarismResultSerializer(many=True, read_only=True)
    type_document_display = serializers.CharField(source='get_type_document_display', read_only=True)
    statut_display = serializers.CharField(source='get_statut_display', read_only=True)
    statut_color = serializers.CharField(source='get_statut_display_color', read_only=True)
    
    class Meta:
        model = Report
        fields = [
            'id', 'titre', 'type_document', 'type_document_display',
            'etudiant', 'fichier', 'fichier_nom_original',
            'statut', 'statut_display', 'statut_color',
            'valide_par_chef', 'date_validation_chef',
            'valide_par_da', 'date_validation_da',
            'rejete_par', 'motif_rejet', 'date_rejet',
            'pdf_signe', 'departement', 'nombre_pages', 'nombre_mots',
            'score_plagiat_global', 'est_plagiat', 'est_test_prive',
            'chapters', 'plagiarism_results',
            'date_soumission', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'etudiant', 'departement', 'nombre_pages', 'nombre_mots',
            'score_plagiat_global', 'est_plagiat', 'created_at', 'updated_at'
        ]


class ReportCreateSerializer(serializers.ModelSerializer):
    """
    Sérialiseur pour la création d'un rapport.
    """
    fichier = serializers.FileField(required=True)
    
    class Meta:
        model = Report
        fields = [
            'id', 'titre', 'type_document', 'fichier', 'est_test_prive'
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
        
        # Vérifier la taille (max 10MB)
        if value.size > 10 * 1024 * 1024:
            raise serializers.ValidationError("Le fichier ne doit pas dépasser 10MB.")
        
        return value


class ReportUpdateSerializer(serializers.ModelSerializer):
    """
    Sérialiseur pour la mise à jour d'un rapport.
    """
    class Meta:
        model = Report
        fields = ['titre', 'type_document']


class ReportValidationSerializer(serializers.Serializer):
    """
    Sérialiseur pour la validation d'un rapport.
    """
    action = serializers.ChoiceField(choices=['valider', 'rejeter'])
    motif_rejet = serializers.CharField(required=False, allow_blank=True)
    
    def validate(self, attrs):
        if attrs['action'] == 'rejeter' and not attrs.get('motif_rejet'):
            raise serializers.ValidationError(
                {"motif_rejet": "Le motif de rejet est obligatoire."}
            )
        return attrs


class PlagiarismTestSerializer(serializers.Serializer):
    """
    Sérialiseur pour lancer un test de plagiat.
    """
    type_detection = serializers.ChoiceField(
        choices=PlagiarismResult.TypeDetection.choices,
        default='PAR_CHAPITRE'
    )
    chapitres_specifiques = serializers.ListField(
        child=serializers.IntegerField(),
        required=False,
        help_text="Liste des numéros de chapitres à tester (optionnel)"
    )


class ReportSubmitSerializer(serializers.Serializer):
    """
    Sérialiseur pour soumettre un rapport.
    """
    confirmation = serializers.BooleanField(required=True)

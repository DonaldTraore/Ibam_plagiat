from django.contrib import admin
from .models import Report, ReportChapter, PlagiarismResult


class ReportChapterInline(admin.TabularInline):
    model = ReportChapter
    extra = 0
    readonly_fields = ['numero_chapitre', 'nombre_mots', 'score_plagiat']


@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = [
        'titre', 'etudiant', 'type_document', 'statut',
        'score_plagiat_global', 'est_plagiat', 'date_soumission'
    ]
    list_filter = [
        'statut', 'type_document', 'departement',
        'est_plagiat', 'created_at'
    ]
    search_fields = [
        'titre', 'etudiant__first_name', 'etudiant__last_name',
        'etudiant__email', 'matricule'
    ]
    readonly_fields = [
        'etudiant', 'departement', 'score_plagiat_global',
        'est_plagiat', 'nombre_mots', 'nombre_pages'
    ]
    inlines = [ReportChapterInline]
    
    fieldsets = (
        ('Informations générales', {
            'fields': ('titre', 'type_document', 'etudiant', 'departement')
        }),
        ('Fichier', {
            'fields': ('fichier', 'fichier_nom_original', 'pdf_signe')
        }),
        ('Statut', {
            'fields': ('statut', 'est_test_prive')
        }),
        ('Validations', {
            'fields': (
                'valide_par_chef', 'date_validation_chef',
                'valide_par_da', 'date_validation_da'
            )
        }),
        ('Rejet', {
            'fields': ('rejete_par', 'motif_rejet', 'date_rejet')
        }),
        ('Métadonnées', {
            'fields': ('nombre_pages', 'nombre_mots', 'score_plagiat_global', 'est_plagiat')
        }),
        ('Dates', {
            'fields': ('date_soumission', 'created_at', 'updated_at')
        }),
    )


@admin.register(ReportChapter)
class ReportChapterAdmin(admin.ModelAdmin):
    list_display = ['report', 'numero_chapitre', 'titre_chapitre', 'nombre_mots', 'score_plagiat']
    list_filter = ['numero_chapitre', 'created_at']
    search_fields = ['report__titre', 'titre_chapitre']
    readonly_fields = ['nombre_mots', 'score_plagiat']


@admin.register(PlagiarismResult)
class PlagiarismResultAdmin(admin.ModelAdmin):
    list_display = ['report', 'type_detection', 'score_global', 'depasse_seuil', 'date_test', 'teste_par']
    list_filter = ['type_detection', 'est_valide', 'date_test']
    search_fields = ['report__titre', 'teste_par__email']
    readonly_fields = ['score_global', 'depasse_seuil']
    filter_horizontal = ['documents_reference']

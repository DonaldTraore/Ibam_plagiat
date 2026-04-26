from django.contrib import admin
from .models import Theme


@admin.register(Theme)
class ThemeAdmin(admin.ModelAdmin):
    list_display = [
        'titre', 'etudiant', 'statut', 'score_similarite',
        'date_soumission', 'created_at'
    ]
    list_filter = ['statut', 'departement', 'created_at']
    search_fields = [
        'titre', 'description', 'mots_cles',
        'etudiant__first_name', 'etudiant__last_name', 'etudiant__email'
    ]
    readonly_fields = ['etudiant', 'departement', 'score_similarite', 'themes_similaires']
    
    fieldsets = (
        ('Informations générales', {
            'fields': ('titre', 'description', 'mots_cles', 'etudiant', 'departement')
        }),
        ('Fichier', {
            'fields': ('fichier',)
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
        ('Similarité', {
            'fields': ('score_similarite', 'themes_similaires')
        }),
        ('Dates', {
            'fields': ('date_soumission', 'created_at', 'updated_at')
        }),
    )

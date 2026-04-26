from django.contrib import admin
from .models import ReferenceDocument


@admin.register(ReferenceDocument)
class ReferenceDocumentAdmin(admin.ModelAdmin):
    list_display = [
        'titre', 'auteur', 'type_document', 'annee',
        'departement', 'nombre_mots', 'est_actif', 'date_ajout'
    ]
    list_filter = ['type_document', 'departement', 'annee', 'est_actif', 'date_ajout']
    search_fields = ['titre', 'auteur', 'description', 'mots_cles']
    readonly_fields = ['ajoute_par', 'nombre_pages', 'nombre_mots', 'contenu_extrait', 'date_ajout']
    
    fieldsets = (
        ('Informations générales', {
            'fields': ('titre', 'auteur', 'annee', 'description')
        }),
        ('Fichier', {
            'fields': ('fichier', 'fichier_nom_original')
        }),
        ('Classification', {
            'fields': ('type_document', 'departement', 'mots_cles', 'est_actif')
        }),
        ('Métadonnées', {
            'fields': ('nombre_pages', 'nombre_mots', 'contenu_extrait')
        }),
        ('Informations système', {
            'fields': ('ajoute_par', 'date_ajout')
        }),
    )

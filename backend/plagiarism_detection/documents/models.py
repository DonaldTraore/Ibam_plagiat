from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


def reference_document_path(instance, filename):
    """Génère le chemin de stockage pour un document de référence."""
    ext = filename.split('.')[-1]
    return f'reference_documents/{instance.departement}/{instance.type_document}/{instance.id}/document.{ext}'


class ReferenceDocument(models.Model):
    """
    Modèle pour les documents de référence utilisés pour la détection de plagiat.
    Ces documents sont ajoutés par la secrétaire ou les enseignants.
    """
    class TypeDocument(models.TextChoices):
        MEMOIRE = 'MEMOIRE', 'Mémoire de Licence'
        MASTER = 'MASTER', 'Mémoire de Master'
        THESE = 'THESE', 'Thèse de Doctorat'
        DOCTORAT = 'DOCTORAT', 'Doctorat'
        ARTICLE = 'ARTICLE', 'Article scientifique'
        RAPPORT = 'RAPPORT', 'Rapport technique'
        AUTRE = 'AUTRE', 'Autre'
    
    titre = models.CharField(max_length=500, verbose_name='Titre du document')
    auteur = models.CharField(
        max_length=255,
        blank=True,
        verbose_name='Auteur(s)'
    )
    annee = models.IntegerField(
        null=True,
        blank=True,
        verbose_name='Année de publication'
    )
    description = models.TextField(
        blank=True,
        verbose_name='Description'
    )
    
    # Fichier
    fichier = models.FileField(
        upload_to=reference_document_path,
        verbose_name='Fichier',
        help_text='Formats acceptés: PDF, DOCX, TXT'
    )
    fichier_nom_original = models.CharField(
        max_length=255,
        blank=True,
        verbose_name='Nom original du fichier'
    )
    
    # Type et classification
    type_document = models.CharField(
        max_length=20,
        choices=TypeDocument.choices,
        default=TypeDocument.AUTRE,
        verbose_name='Type de document'
    )
    departement = models.CharField(
        max_length=20,
        choices=User.Departement.choices,
        verbose_name='Département'
    )
    mots_cles = models.CharField(
        max_length=500,
        blank=True,
        verbose_name='Mots-clés',
        help_text='Mots-clés séparés par des virgules'
    )
    
    # Métadonnées du document
    nombre_pages = models.IntegerField(null=True, blank=True, verbose_name='Nombre de pages')
    nombre_mots = models.IntegerField(null=True, blank=True, verbose_name='Nombre de mots')
    
    # Extraction du contenu (stocké pour la comparaison rapide)
    contenu_extrait = models.TextField(
        blank=True,
        verbose_name='Contenu extrait',
        help_text='Contenu textuel extrait du document pour la comparaison'
    )
    
    # Utilisateur qui a ajouté le document
    ajoute_par = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='documents_ajoutes',
        verbose_name='Ajouté par'
    )
    
    # Statut
    est_actif = models.BooleanField(
        default=True,
        verbose_name='Actif',
        help_text='Si False, ce document ne sera pas utilisé pour la comparaison'
    )
    
    # Dates
    date_ajout = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Document de référence'
        verbose_name_plural = 'Documents de référence'
        ordering = ['-date_ajout']
    
    def __str__(self):
        return f"{self.titre} ({self.get_type_document_display()})"
    
    def save(self, *args, **kwargs):
        if not self.fichier_nom_original and self.fichier:
            self.fichier_nom_original = self.fichier.name
        super().save(*args, **kwargs)

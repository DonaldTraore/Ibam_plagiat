from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()


def theme_file_path(instance, filename):
    """Génère le chemin de stockage pour un fichier de thème."""
    ext = filename.split('.')[-1]
    return f'themes/{instance.etudiant.id}/{instance.id}/theme.{ext}'


class Theme(models.Model):
    """
    Modèle représentant un thème de recherche proposé par un étudiant.
    """
    class Statut(models.TextChoices):
        BROUILLON = 'BROUILLON', 'Brouillon'
        SOUMIS = 'SOUMIS', 'Soumis'
        EN_REVUE_CHEF = 'EN_REVUE_CHEF', 'En révision (Chef de département)'
        EN_REVUE_DA = 'EN_REVUE_DA', 'En révision (DA)'
        VALIDE = 'VALIDE', 'Validé'
        REJETE_CHEF = 'REJETE_CHEF', 'Rejeté par le Chef de département'
        REJETE_DA = 'REJETE_DA', 'Rejeté par le DA'
        REJETE_DEFINITIF = 'REJETE_DEFINITIF', 'Rejeté définitivement'
    
    # Informations de base
    titre = models.CharField(max_length=500, verbose_name='Titre du thème')
    description = models.TextField(verbose_name='Description du thème')
    mots_cles = models.CharField(
        max_length=500,
        blank=True,
        verbose_name='Mots-clés',
        help_text='Mots-clés séparés par des virgules'
    )
    
    # Étudiant
    etudiant = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='themes',
        limit_choices_to={'role': 'ETUDIANT'},
        verbose_name='Étudiant'
    )
    
    # Fichier optionnel (résumé, proposition, etc.)
    fichier = models.FileField(
        upload_to=theme_file_path,
        blank=True,
        null=True,
        verbose_name='Fichier complémentaire'
    )
    
    # Statut et workflow
    statut = models.CharField(
        max_length=20,
        choices=Statut.choices,
        default=Statut.BROUILLON,
        verbose_name='Statut'
    )
    
    # Validations
    valide_par_chef = models.BooleanField(default=False, verbose_name='Validé par le Chef')
    date_validation_chef = models.DateTimeField(null=True, blank=True, verbose_name='Date validation Chef')
    
    valide_par_da = models.BooleanField(default=False, verbose_name='Validé par le DA')
    date_validation_da = models.DateTimeField(null=True, blank=True, verbose_name='Date validation DA')
    
    # Rejet
    rejete_par = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='themes_rejetes',
        verbose_name='Rejeté par'
    )
    motif_rejet = models.TextField(blank=True, null=True, verbose_name='Motif de rejet')
    date_rejet = models.DateTimeField(null=True, blank=True, verbose_name='Date du rejet')
    
    # Département
    departement = models.CharField(
        max_length=20,
        choices=User.Departement.choices,
        verbose_name='Département'
    )
    
    # Informations de test
    est_test_prive = models.BooleanField(
        default=False,
        verbose_name='Est un test privé'
    )
    
    # Résultats de test de similarité
    score_similarite = models.FloatField(
        default=0.0,
        verbose_name='Score de similarité (%)',
        help_text='Pourcentage de similarité avec les thèmes existants'
    )
    themes_similaires = models.JSONField(
        default=list,
        blank=True,
        verbose_name='Thèmes similaires trouvés'
    )
    
    # Dates
    date_soumission = models.DateTimeField(null=True, blank=True, verbose_name='Date de soumission')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Thème'
        verbose_name_plural = 'Thèmes'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.titre} - {self.etudiant.get_full_name()}"
    
    def save(self, *args, **kwargs):
        # Définir le département automatiquement
        if not self.departement and self.etudiant:
            self.departement = self.etudiant.departement
        super().save(*args, **kwargs)
    
    @property
    def get_statut_display_color(self):
        """Retourne une couleur pour l'affichage du statut."""
        colors = {
            'BROUILLON': 'gray',
            'SOUMIS': 'blue',
            'EN_REVUE_CHEF': 'orange',
            'EN_REVUE_DA': 'purple',
            'VALIDE': 'green',
            'REJETE_CHEF': 'red',
            'REJETE_DA': 'red',
            'REJETE_DEFINITIF': 'darkred',
        }
        return colors.get(self.statut, 'gray')
    
    def soumettre(self):
        """Soumet le thème pour validation."""
        self.statut = self.Statut.SOUMIS
        self.date_soumission = timezone.now()
        self.est_test_prive = False
        self.save()
    
    def valider_par_chef(self, chef):
        """Valide le thème par le chef de département."""
        self.valide_par_chef = True
        self.date_validation_chef = timezone.now()
        self.statut = self.Statut.EN_REVUE_DA
        self.save()
    
    def rejeter_par_chef(self, chef, motif):
        """Rejette le thème par le chef de département."""
        self.rejete_par = chef
        self.motif_rejet = motif
        self.date_rejet = timezone.now()
        self.statut = self.Statut.REJETE_CHEF
        self.save()
    
    def valider_par_da(self, da):
        """Valide définitivement le thème par le DA."""
        self.valide_par_da = True
        self.date_validation_da = timezone.now()
        self.statut = self.Statut.VALIDE
        self.save()
    
    def rejeter_par_da(self, da, motif):
        """Rejette définitivement le thème par le DA."""
        self.rejete_par = da
        self.motif_rejet = motif
        self.date_rejet = timezone.now()
        self.statut = self.Statut.REJETE_DEFINITIF
        self.save()

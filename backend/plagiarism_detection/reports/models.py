from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
import os

User = get_user_model()


def report_file_path(instance, filename):
    """
    Génère le chemin de stockage pour un fichier de rapport.
    """
    ext = filename.split('.')[-1]
    return f'reports/{instance.etudiant.id}/{instance.id}/rapport.{ext}'


def signed_pdf_path(instance, filename):
    """
    Génère le chemin de stockage pour un PDF signé.
    """
    return f'reports/{instance.etudiant.id}/{instance.id}/rapport_signe.pdf'


class Report(models.Model):
    """
    Modèle représentant un rapport (mémoire, thèse, master, doctorat).
    """
    class TypeDocument(models.TextChoices):
        MEMOIRE = 'MEMOIRE', 'Mémoire de Licence'
        MASTER = 'MASTER', 'Mémoire de Master'
        THESE = 'THESE', 'Thèse de Doctorat'
        DOCTORAT = 'DOCTORAT', 'Doctorat'
        
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
    titre = models.CharField(max_length=500, verbose_name='Titre du rapport')
    type_document = models.CharField(
        max_length=20,
        choices=TypeDocument.choices,
        default=TypeDocument.MEMOIRE,
        verbose_name='Type de document'
    )
    
    # Étudiant
    etudiant = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='reports',
        limit_choices_to={'role': 'ETUDIANT'},
        verbose_name='Étudiant'
    )
    
    # Fichier
    fichier = models.FileField(
        upload_to=report_file_path,
        verbose_name='Fichier du rapport',
        help_text='Formats acceptés: PDF, DOCX, TXT'
    )
    fichier_nom_original = models.CharField(
        max_length=255,
        blank=True,
        verbose_name='Nom original du fichier'
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
        related_name='reports_rejetes',
        verbose_name='Rejeté par'
    )
    motif_rejet = models.TextField(blank=True, null=True, verbose_name='Motif de rejet')
    date_rejet = models.DateTimeField(null=True, blank=True, verbose_name='Date du rejet')
    
    # PDF signé (pour validation finale)
    pdf_signe = models.FileField(
        upload_to=signed_pdf_path,
        blank=True,
        null=True,
        verbose_name='PDF signé et tamponné'
    )
    
    # Département
    departement = models.CharField(
        max_length=20,
        choices=User.Departement.choices,
        verbose_name='Département'
    )
    
    # Métadonnées du document
    nombre_pages = models.IntegerField(null=True, blank=True, verbose_name='Nombre de pages')
    nombre_mots = models.IntegerField(null=True, blank=True, verbose_name='Nombre de mots')
    
    # Résultats de détection de plagiat
    score_plagiat_global = models.FloatField(
        default=0.0,
        verbose_name='Score de plagiat global (%)'
    )
    est_plagiat = models.BooleanField(default=False, verbose_name='Est considéré comme plagiat')
    
    # Informations de test (pour les tests privés des étudiants)
    est_test_prive = models.BooleanField(
        default=False,
        verbose_name='Est un test privé'
    )
    
    # Dates
    date_soumission = models.DateTimeField(null=True, blank=True, verbose_name='Date de soumission')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Rapport'
        verbose_name_plural = 'Rapports'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.titre} - {self.etudiant.get_full_name()}"
    
    def save(self, *args, **kwargs):
        # Définir le département automatiquement
        if not self.departement and self.etudiant:
            self.departement = self.etudiant.departement
        
        # Définir le statut en fonction des validations
        if self.valide_par_da:
            self.statut = self.Statut.VALIDE
        elif self.rejete_par and self.rejete_par.is_da:
            self.statut = self.Statut.REJETE_DA
        
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
        """Soumet le rapport pour validation."""
        self.statut = self.Statut.SOUMIS
        self.date_soumission = timezone.now()
        self.est_test_prive = False
        self.save()
    
    def valider_par_chef(self, chef):
        """Valide le rapport par le chef de département."""
        self.valide_par_chef = True
        self.date_validation_chef = timezone.now()
        self.statut = self.Statut.EN_REVUE_DA
        self.save()
    
    def rejeter_par_chef(self, chef, motif):
        """Rejette le rapport par le chef de département."""
        self.rejete_par = chef
        self.motif_rejet = motif
        self.date_rejet = timezone.now()
        self.statut = self.Statut.REJETE_CHEF
        self.save()
    
    def valider_par_da(self, da):
        """Valide définitivement le rapport par le DA."""
        self.valide_par_da = True
        self.date_validation_da = timezone.now()
        self.statut = self.Statut.VALIDE
        self.save()
    
    def rejeter_par_da(self, da, motif):
        """Rejette définitivement le rapport par le DA."""
        self.rejete_par = da
        self.motif_rejet = motif
        self.date_rejet = timezone.now()
        self.statut = self.Statut.REJETE_DEFINITIF
        self.save()


class ReportChapter(models.Model):
    """
    Modèle représentant un chapitre d'un rapport pour la détection de plagiat par chapitre.
    """
    report = models.ForeignKey(
        Report,
        on_delete=models.CASCADE,
        related_name='chapters',
        verbose_name='Rapport'
    )
    
    numero_chapitre = models.IntegerField(verbose_name='Numéro du chapitre')
    titre_chapitre = models.CharField(
        max_length=255,
        blank=True,
        verbose_name='Titre du chapitre'
    )
    contenu = models.TextField(verbose_name='Contenu du chapitre')
    nombre_mots = models.IntegerField(verbose_name='Nombre de mots')
    
    # Résultats de plagiat pour ce chapitre
    score_plagiat = models.FloatField(
        default=0.0,
        verbose_name='Score de plagiat (%)'
    )
    passages_plagies = models.JSONField(
        default=list,
        blank=True,
        verbose_name='Passages plagiés détectés',
        help_text='Liste des passages plagiés avec leurs sources'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Chapitre de Rapport'
        verbose_name_plural = 'Chapitres de Rapports'
        ordering = ['numero_chapitre']
        unique_together = ['report', 'numero_chapitre']
    
    def __str__(self):
        return f"Chapitre {self.numero_chapitre} - {self.report.titre}"


class PlagiarismResult(models.Model):
    """
    Modèle stockant les résultats détaillés de la détection de plagiat.
    """
    class TypeDetection(models.TextChoices):
        PAR_CHAPITRE = 'PAR_CHAPITRE', 'Détection par chapitre'
        GLOBAL = 'GLOBAL', 'Détection globale'
    
    report = models.ForeignKey(
        Report,
        on_delete=models.CASCADE,
        related_name='plagiarism_results',
        verbose_name='Rapport'
    )
    
    type_detection = models.CharField(
        max_length=20,
        choices=TypeDetection.choices,
        default=TypeDetection.PAR_CHAPITRE,
        verbose_name='Type de détection'
    )
    
    # Scores
    score_global = models.FloatField(verbose_name='Score de plagiat global (%)')
    score_par_chapitre = models.JSONField(
        default=dict,
        blank=True,
        verbose_name='Scores par chapitre'
    )
    
    # Détails des similitudes
    similitudes_trouvees = models.JSONField(
        default=list,
        verbose_name='Similitudes trouvées',
        help_text='Liste détaillée des similitudes avec sources'
    )
    
    # Documents de référence utilisés pour la comparaison
    documents_reference = models.ManyToManyField(
        'documents.ReferenceDocument',
        blank=True,
        related_name='plagiarism_results',
        verbose_name='Documents de référence'
    )
    
    # Informations sur le test
    teste_par = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='Testé par'
    )
    date_test = models.DateTimeField(auto_now_add=True, verbose_name='Date du test')
    
    # Statut du résultat
    est_valide = models.BooleanField(
        default=True,
        verbose_name='Résultat valide'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Résultat de Plagiat'
        verbose_name_plural = 'Résultats de Plagiat'
        ordering = ['-date_test']
    
    def __str__(self):
        return f"Résultat plagiat - {self.report.titre} ({self.score_global}%)"
    
    @property
    def depasse_seuil(self):
        """Vérifie si le score dépasse le seuil de 25%."""
        from django.conf import settings
        return self.score_global > getattr(settings, 'PLAGIARISM_THRESHOLD', 25)

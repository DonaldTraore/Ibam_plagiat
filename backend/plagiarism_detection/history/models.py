from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class History(models.Model):
    """
    Modèle pour l'historique des actions (traçabilité).
    """
    class Action(models.TextChoices):
        CREATION = 'CREATION', 'Création'
        MODIFICATION = 'MODIFICATION', 'Modification'
        SOUMISSION = 'SOUMISSION', 'Soumission'
        VALIDATION = 'VALIDATION', 'Validation'
        REJET = 'REJET', 'Rejet'
        SUPPRESSION = 'SUPPRESSION', 'Suppression'
        TEST_PLAGIAT = 'TEST_PLAGIAT', 'Test de plagiat'
        TELECHARGEMENT = 'TELECHARGEMENT', 'Téléchargement'
    
    class EntityType(models.TextChoices):
        REPORT = 'REPORT', 'Rapport'
        THEME = 'THEME', 'Thème'
        DOCUMENT = 'DOCUMENT', 'Document'
        USER = 'USER', 'Utilisateur'
    
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='history_entries',
        verbose_name='Utilisateur'
    )
    action = models.CharField(
        max_length=20,
        choices=Action.choices,
        verbose_name='Action'
    )
    entity_type = models.CharField(
        max_length=20,
        choices=EntityType.choices,
        verbose_name='Type d\'entité'
    )
    entity_id = models.IntegerField(
        null=True,
        blank=True,
        verbose_name='ID de l\'entité'
    )
    details = models.TextField(
        verbose_name='Détails',
        help_text='Description détaillée de l\'action'
    )
    ip_address = models.GenericIPAddressField(
        null=True,
        blank=True,
        verbose_name='Adresse IP'
    )
    user_agent = models.TextField(
        blank=True,
        verbose_name='User Agent'
    )
    departement = models.CharField(
        max_length=20,
        choices=User.Departement.choices,
        blank=True,
        verbose_name='Département'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Entrée d\'historique'
        verbose_name_plural = 'Historique'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.action} - {self.entity_type} ({self.user.get_full_name()})"

from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Notification(models.Model):
    """
    Modèle pour les notifications.
    """
    class TypeNotification(models.TextChoices):
        NOUVEAU_RAPPORT = 'NOUVEAU_RAPPORT', 'Nouveau rapport soumis'
        NOUVEAU_THEME = 'NOUVEAU_THEME', 'Nouveau thème soumis'
        RAPPORT_VALIDE = 'RAPPORT_VALIDE', 'Rapport validé'
        THEME_VALIDE = 'THEME_VALIDE', 'Thème validé'
        RAPPORT_REJETE = 'RAPPORT_REJETE', 'Rapport rejeté'
        THEME_REJETE = 'THEME_REJETE', 'Thème rejeté'
        RAPPORT_REJETE_DA = 'RAPPORT_REJETE_DA', 'Rapport rejeté par le DA'
        THEME_REJETE_DA = 'THEME_REJETE_DA', 'Thème rejeté par le DA'
        RAPPORT_REJETE_DEFINITIF = 'RAPPORT_REJETE_DEFINITIF', 'Rapport rejeté définitivement'
        THEME_REJETE_DEFINITIF = 'THEME_REJETE_DEFINITIF', 'Thème rejeté définitivement'
        RAPPORT_A_VALIDER = 'RAPPORT_A_VALIDER', 'Rapport à valider'
        THEME_A_VALIDER = 'THEME_A_VALIDER', 'Thème à valider'
        TEST_PLAGIAT_TERMINE = 'TEST_PLAGIAT_TERMINE', 'Test de plagiat terminé'
        PLAGIAT_DETECTE = 'PLAGIAT_DETECTE', 'Plagiat détecté'
        SYSTEME = 'SYSTEME', 'Notification système'
    
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='notifications',
        verbose_name='Destinataire'
    )
    type = models.CharField(
        max_length=30,
        choices=TypeNotification.choices,
        verbose_name='Type'
    )
    titre = models.CharField(max_length=255, verbose_name='Titre')
    message = models.TextField(verbose_name='Message')
    lien = models.URLField(
        blank=True,
        null=True,
        verbose_name='Lien'
    )
    lu = models.BooleanField(default=False, verbose_name='Lu')
    date_lecture = models.DateTimeField(null=True, blank=True, verbose_name='Date de lecture')
    
    # Email
    email_envoye = models.BooleanField(default=False, verbose_name='Email envoyé')
    date_envoi_email = models.DateTimeField(null=True, blank=True, verbose_name='Date envoi email')
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Notification'
        verbose_name_plural = 'Notifications'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.titre} - {self.user.get_full_name()}"
    
    def marquer_comme_lu(self):
        """Marque la notification comme lue."""
        if not self.lu:
            self.lu = True
            self.date_lecture = timezone.now()
            self.save()

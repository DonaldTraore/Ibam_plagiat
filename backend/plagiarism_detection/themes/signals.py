from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Theme
from ..history.models import History


@receiver(post_save, sender=Theme)
def create_history_on_theme_change(sender, instance, created, **kwargs):
    """
    Crée une entrée dans l'historique lors des changements de statut d'un thème.
    """
    if not created:
        action = None
        details = ""
        
        if instance.statut == 'SOUMIS':
            action = 'SOUMISSION'
            details = f"Thème soumis: {instance.titre}"
        elif instance.statut == 'VALIDE':
            action = 'VALIDATION'
            details = f"Thème validé définitivement: {instance.titre}"
        elif 'REJETE' in instance.statut:
            action = 'REJET'
            details = f"Thème rejeté ({instance.statut}): {instance.titre}. Motif: {instance.motif_rejet or 'Non spécifié'}"
        
        if action:
            History.objects.create(
                user=instance.etudiant,
                action=action,
                entity_type='THEME',
                entity_id=instance.id,
                details=details,
                departement=instance.departement
            )

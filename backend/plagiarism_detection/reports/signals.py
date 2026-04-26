from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Report
from ..history.models import History


@receiver(post_save, sender=Report)
def create_history_on_report_change(sender, instance, created, **kwargs):
    """
    Crée une entrée dans l'historique lors des changements de statut d'un rapport.
    """
    if not created:
        # Déterminer l'action effectuée
        action = None
        details = ""
        
        if instance.statut == 'SOUMIS' and hasattr(instance, '_previous_statut') and instance._previous_statut == 'BROUILLON':
            action = 'SOUMISSION'
            details = f"Rapport soumis: {instance.titre}"
        elif instance.statut == 'VALIDE':
            action = 'VALIDATION'
            details = f"Rapport validé définitivement: {instance.titre}"
        elif 'REJETE' in instance.statut:
            action = 'REJET'
            details = f"Rapport rejeté ({instance.statut}): {instance.titre}. Motif: {instance.motif_rejet or 'Non spécifié'}"
        
        if action:
            History.objects.create(
                user=instance.etudiant,
                action=action,
                entity_type='REPORT',
                entity_id=instance.id,
                details=details,
                departement=instance.departement
            )


@receiver(post_save, sender=Report)
def store_previous_statut(sender, instance, **kwargs):
    """
    Stocke le statut précédent pour détecter les changements.
    """
    instance._previous_statut = instance.statut

from django.apps import AppConfig


class AccountsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'plagiarism_detection.accounts'
    verbose_name = 'Gestion des Comptes'

    def ready(self):
        import plagiarism_detection.accounts.signals

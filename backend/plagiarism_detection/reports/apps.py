from django.apps import AppConfig


class ReportsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'plagiarism_detection.reports'
    verbose_name = 'Gestion des Rapports'

    def ready(self):
        import plagiarism_detection.reports.signals

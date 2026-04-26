from django.apps import AppConfig


class ThemesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'plagiarism_detection.themes'
    verbose_name = 'Gestion des Thèmes'

    def ready(self):
        import plagiarism_detection.themes.signals

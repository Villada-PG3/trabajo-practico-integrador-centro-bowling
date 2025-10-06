from django.apps import AppConfig


class BowlConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'bowl'

# bowl/apps.py
from django.apps import AppConfig

class BowlConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'bowl'

    def ready(self):
        import bowl.signals  # conecta los signals

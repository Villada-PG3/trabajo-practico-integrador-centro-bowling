from django.apps import AppConfig

class BowlConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'bowl'

    def ready(self):
        pass  # 👈 Esto conecta las señales al iniciar Django

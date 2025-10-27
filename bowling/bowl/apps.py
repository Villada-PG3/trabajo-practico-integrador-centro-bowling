from django.apps import AppConfig

class BowlConfig(AppConfig):
    # Define que los IDs automáticos serán BigAutoField (entero grande)
    default_auto_field = 'django.db.models.BigAutoField'
    
    # Nombre interno de la aplicación
    name = 'bowl'

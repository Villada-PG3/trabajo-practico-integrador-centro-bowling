from django.apps import AppConfig

class BowlConfig(AppConfig):
    # Define que los IDs automáticos serán BigAutoField (entero grande)
    default_auto_field = 'django.db.models.BigAutoField'
    
    # Nombre interno de la aplicación
    name = 'bowl'

    # Se ejecuta cuando la app se carga; activa las señales
    def ready(self):
<<<<<<< HEAD
        pass  # 👈 Esto conecta las señales al iniciar Django
=======
        import bowl.signals
>>>>>>> f15d8a83d7642d7c398b0061ff5b68592723d23d

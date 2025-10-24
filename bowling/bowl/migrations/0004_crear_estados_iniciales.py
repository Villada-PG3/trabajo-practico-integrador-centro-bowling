from django.db import migrations

def crear_estados(apps, schema_editor):
    Estado = apps.get_model('bowl', 'Estado')
    for nombre in ["Pendiente", "Confirmada", "Cancelada"]:
        Estado.objects.get_or_create(nombre=nombre)

class Migration(migrations.Migration):

    dependencies = [
        ('bowl', '0003_pista_numero'),  # 👈 poné acá el nombre de tu última migración real
    ]

    operations = [
        migrations.RunPython(crear_estados),
    ]

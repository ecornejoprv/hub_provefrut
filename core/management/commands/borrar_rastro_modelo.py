from django.core.management.base import BaseCommand
from django.contrib.contenttypes.models import ContentType

class Command(BaseCommand):
    help = 'Elimina de la BD el rastro (ContentType y Permisos) de un modelo que borraste del código.'

    def add_arguments(self, parser):
        # Le decimos que acepte un argumento: el nombre del modelo
        parser.add_argument('nombre_modelo', type=str, help='El nombre del modelo a borrar (ej: ModuloInventario)')

    def handle(self, *args, **options):
        nombre_modelo = options['nombre_modelo'].lower() # Django guarda todo en minúsculas
        app_label = 'core' # Asumimos que están en la app 'core'

        self.stdout.write(f"Buscando rastro de '{nombre_modelo}' en la BD...")

        try:
            ct = ContentType.objects.get(app_label=app_label, model=nombre_modelo)
            
            # Preguntar confirmación para seguridad
            confirm = input(f"⚠️  Se encontraron permisos asociados a '{nombre_modelo}'. ¿Borrar todo? (s/n): ")
            if confirm.lower() != 's':
                self.stdout.write("Operación cancelada.")
                return

            # Al borrar el ContentType, se borran los permisos en cascada
            ct.delete()
            self.stdout.write(self.style.SUCCESS(f"✅ ÉXITO: Se eliminó '{nombre_modelo}' y todos sus permisos."))

        except ContentType.DoesNotExist:
            self.stdout.write(self.style.WARNING(f"Nada que borrar. El modelo '{nombre_modelo}' no existe en la BD."))
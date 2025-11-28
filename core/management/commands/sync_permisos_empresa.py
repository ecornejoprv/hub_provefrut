from django.core.management.base import BaseCommand
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from core.models import Empresa

class Command(BaseCommand):
    help = 'Limpia permisos viejos colgados de Empresa'

    def handle(self, *args, **options):
        # Buscar ContentType de Empresa
        try:
            ct = ContentType.objects.get_for_model(Empresa)
            # Buscar permisos que NO sean los default de Django
            perms = Permission.objects.filter(content_type=ct).exclude(
                codename__in=['add_empresa', 'change_empresa', 'delete_empresa', 'view_empresa']
            )
            count = perms.count()
            if count > 0:
                print(f"Borrando {count} permisos viejos de Empresa...")
                perms.delete()
                print("¡Limpieza lista!")
            else:
                print("No hay permisos viejos que borrar.")
        except Exception as e:
            print(f"Error: {e}")
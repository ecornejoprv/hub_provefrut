from django.core.management.base import BaseCommand
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType

# 1. IMPORTS: Solo traemos los modelos que existen realmente en models.py
# (Ya quitamos ModuloInventario de aquí)
from core.models import (
    ModuloChatbot, 
    ModuloCompras, 
    ModuloSistema
)

class Command(BaseCommand):
    help = 'Sincroniza permisos de TODOS los módulos definidos (Crea, Actualiza y Pura)'

    def handle(self, *args, **options):
        self.stdout.write("Iniciando Sincronización Maestra de Permisos...")

        # 2. LISTA MAESTRA: Solo los modelos activos
        # (Ya quitamos ModuloInventario de aquí también)
        MODELOS_A_SINCRONIZAR = [
            ModuloChatbot,
            ModuloCompras,
            ModuloSistema,
        ]

        total_creados = 0
        total_borrados = 0

        # 3. EL BUCLE (Lógica Genérica - No cambia)
        for modelo_clase in MODELOS_A_SINCRONIZAR:
            nombre_modelo = modelo_clase.__name__
            self.stdout.write(f"\nProcesando: {nombre_modelo}...")

            try:
                # Obtener ContentType
                ct = ContentType.objects.get_for_model(modelo_clase)
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Error obteniendo ContentType para {nombre_modelo}: {e}"))
                continue

            # Obtener permisos del código
            permisos_codigo = dict(modelo_clase._meta.permissions)
            
            # A. CREAR O ACTUALIZAR
            codenames_activos = []
            for codename, name in permisos_codigo.items():
                obj, created = Permission.objects.update_or_create(
                    codename=codename,
                    content_type=ct,
                    defaults={'name': name}
                )
                codenames_activos.append(codename)
                if created:
                    self.stdout.write(self.style.SUCCESS(f"  [+] Creado: {codename}"))
                    total_creados += 1

            # B. BORRAR ZOMBIES (Dentro de este módulo específico)
            zombies = Permission.objects.filter(content_type=ct).exclude(
                codename__in=codenames_activos
            )
            
            count_zombies = zombies.count()
            if count_zombies > 0:
                self.stdout.write(self.style.WARNING(f"  [-] Eliminando {count_zombies} permisos obsoletos..."))
                zombies.delete()
                total_borrados += 1
            else:
                self.stdout.write(self.style.SUCCESS("  [OK] Limpio."))

        # RESUMEN FINAL
        self.stdout.write(self.style.SUCCESS(f"\n--- PROCESO TERMINADO ---"))
        self.stdout.write(f"Permisos Nuevos: {total_creados}")
        self.stdout.write(f"Permisos Borrados: {total_borrados}")
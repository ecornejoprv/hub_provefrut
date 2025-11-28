from django.db import models
from django.contrib.auth.models import User, Group, Permission

# =================================================================
# 1. ESTRUCTURA ORGANIZACIONAL (ÁREAS)
# =================================================================
class Area(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    codigo = models.CharField(max_length=20, unique=True, help_text="Ej: FIN, LOG, IT")
    
    def __str__(self):
        return self.nombre

# =================================================================
# 2. EXTENSIÓN DE GRUPOS (CARGOS)
# =================================================================
class PerfilGrupo(models.Model):
    grupo = models.OneToOneField(Group, on_delete=models.CASCADE, related_name='perfil')
    area = models.ForeignKey(Area, on_delete=models.CASCADE)
    es_gerencial = models.BooleanField(default=False, help_text="Si es True, este rol puede gestionar a otros.")

    def __str__(self):
        return f"{self.grupo.name} ({self.area.nombre})"

# =================================================================
# 3. MODELOS FANTASMA (CONTENEDORES DE PERMISOS)
# =================================================================
# Estos modelos NO crean tablas (managed=False).
# Sirven solo para agrupar permisos por Aplicativo.

class ModuloChatbot(models.Model):
    class Meta:
        managed = False  # No busca tabla en BD
        default_permissions = () # Sin add/change/delete automáticos
        permissions = [
            ("chatbot_acceso", "CHATBOT: Acceso para interactuar"),
            ("chatbot_admin", "CHATBOT: Ver logs y entrenar"),
        ]

class ModuloCompras(models.Model):
    class Meta:
        managed = False
        default_permissions = ()
        permissions = [
            ("compras_acceso", "COMPRAS: Ingreso al módulo"),
            ("compras_crear_orden", "COMPRAS: Crear órdenes"),
            ("compras_aprobar_orden", "COMPRAS: Aprobar órdenes (Jefatura)"),
            ("compras_ver_reportes", "COMPRAS: Ver reportes financieros"),
        ]
        
class ModuloSistema(models.Model):
    class Meta:
        managed = False
        default_permissions = ()
        permissions = [
             ("sistema_gestion_usuarios", "SISTEMA: Gestión de usuarios"),
        ]

# =================================================================
# 4. EMPRESAS (Limpias de permisos)
# =================================================================
class Empresa(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    codigo = models.CharField(max_length=10, unique=True)
    activo = models.BooleanField(default=True)

    # Nota: Ya no ponemos class Meta con permissions aquí.

    def __str__(self):
        return f"{self.nombre} ({self.codigo})"

# =================================================================
# 5. MATRIZ DE ASIGNACIÓN (PERTENENCIA)
# =================================================================
class Pertenencia(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='pertenencias')
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE)
    grupo = models.ForeignKey(Group, on_delete=models.CASCADE)
    area = models.ForeignKey(Area, on_delete=models.SET_NULL, null=True, blank=True)

    permisos_adicionales = models.ManyToManyField(
        Permission, 
        blank=True, 
        help_text="Excepciones específicas para este usuario en esta empresa."
    )

    class Meta:
        unique_together = ('usuario', 'empresa')
        verbose_name = "Asignación de Rol"
        verbose_name_plural = "Asignaciones de Roles"

    def __str__(self):
        return f"{self.usuario.username} -> {self.empresa.codigo} [{self.grupo.name}]"

# =================================================================
# 6. AUDITORÍA
# =================================================================
class HistorialCambiosRol(models.Model):
    fecha = models.DateTimeField(auto_now_add=True)
    actor = models.ForeignKey(User, related_name='auditoria_actor', on_delete=models.PROTECT)
    usuario_afectado = models.ForeignKey(User, related_name='auditoria_afectado', on_delete=models.PROTECT)
    accion = models.CharField(max_length=255)
    detalle = models.TextField()
    
    def __str__(self):
        return f"{self.fecha} - {self.actor} modificó a {self.usuario_afectado}"
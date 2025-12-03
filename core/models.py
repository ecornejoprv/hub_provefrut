"""
CORE MODELS - ARQUITECTURA DE DATOS
-----------------------------------
Este archivo define la estructura de la base de datos del Hub de Identidad.

ARQUITECTURA:
1. Multi-Empresa: Los usuarios no tienen un rol único, tienen 'Pertenencias' por empresa.
2. Roles Extendidos: Los Grupos de Django se extienden para pertenecer a Áreas (Deptos).
3. Permisos Modulares: Usamos 'Modelos Fantasma' (managed=False) para agrupar permisos
   por dominio de negocio (Compras, Chatbot, etc.) sin crear tablas innecesarias.
4. Seguridad: Auditoría de cambios y perfiles de seguridad extendidos.
"""

from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User, Group, Permission

# ==============================================================================
# 1. ESTRUCTURA ORGANIZACIONAL
# ==============================================================================
class Area(models.Model):
    """
    Representa un departamento funcional o territorio dentro de la corporación.
    Ejemplos: "Dirección Financiera", "Logística y Bodega", "Tecnología".
    """
    nombre = models.CharField(max_length=100, unique=True)
    codigo = models.CharField(
        max_length=20, 
        unique=True, 
        help_text="Código corto para referencias internas. Ej: FIN, LOG, IT"
    )
    
    def __str__(self):
        return self.nombre


# ==============================================================================
# 2. EXTENSIÓN DE ROLES (CARGOS)
# ==============================================================================
class PerfilGrupo(models.Model):
    """
    Extiende el modelo 'Group' nativo de Django.
    
    OBJETIVO:
    Django por defecto tiene grupos planos. Aquí les damos contexto organizacional.
    Esto permite decir: "El grupo JEFE_BODEGA pertenece al área LOGÍSTICA".
    """
    grupo = models.OneToOneField(Group, on_delete=models.CASCADE, related_name='perfil')
    area = models.ForeignKey(Area, on_delete=models.CASCADE)
    
    es_gerencial = models.BooleanField(
        default=False, 
        help_text="Si es True, este rol tiene capacidades de gestión sobre subordinados."
    )

    def __str__(self):
        return f"{self.grupo.name} ({self.area.nombre})"


# ==============================================================================
# 3. MODELOS FANTASMA (CONTENEDORES DE PERMISOS)
# ==============================================================================
# ESTRATEGIA:
# Estos modelos tienen `managed = False`. No crean tablas en la base de datos.
# Sirven exclusivamente como 'namespaces' para organizar los permisos en el Admin
# y desacoplar la lógica de permisos de los modelos físicos.

class ModuloChatbot(models.Model):
    """
    Contenedor de permisos para el Asistente Virtual (IA).
    """
    class Meta:
        managed = False  # No impacta la BD
        default_permissions = ()  # Sin add/change/delete automáticos
        permissions = [
            ("chatbot_acceso", "CHATBOT: Acceso para interactuar"),
            ("chatbot_admin", "CHATBOT: Ver logs y entrenar"),
        ]

class ModuloCompras(models.Model):
    """
    Contenedor de permisos para el Sistema de Adquisiciones.
    """
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
    """
    Contenedor de permisos para Administración General del Hub.
    """
    class Meta:
        managed = False
        default_permissions = ()
        permissions = [
             ("sistema_gestion_usuarios", "SISTEMA: Gestión de usuarios"),
        ]


# ==============================================================================
# 4. ENTIDADES (TENANTS)
# ==============================================================================
class Empresa(models.Model):
    """
    Representa una entidad legal o unidad de negocio independiente.
    Ej: Provefrut, Nintanga, Procongelados.
    """
    nombre = models.CharField(max_length=100, unique=True)
    codigo = models.CharField(max_length=10, unique=True)
    activo = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.nombre} ({self.codigo})"


# ==============================================================================
# 5. NÚCLEO DE IDENTIDAD (LA MATRIZ)
# ==============================================================================
class Pertenencia(models.Model):
    """
    MODELO CRÍTICO: Matriz de Asignación.
    
    Define la relación: QUIÉN (Usuario) -> QUÉ ES (Rol/Grupo) -> DÓNDE (Empresa).
    
    Esta arquitectura permite que una persona sea 'Jefe' en la Empresa A
    y 'Consultor' en la Empresa B sin duplicar su usuario.
    """
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='pertenencias')
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE)
    
    # El Cargo Base (trae los permisos estándar definidos en el Grupo)
    grupo = models.ForeignKey(Group, on_delete=models.CASCADE)
    
    # Redundancia controlada para búsquedas rápidas por área
    area = models.ForeignKey(Area, on_delete=models.SET_NULL, null=True, blank=True)

    # Excepciones: Permisos "Granulares" extra para este usuario específico en esta empresa
    permisos_adicionales = models.ManyToManyField(
        Permission, 
        blank=True, 
        help_text="Excepciones específicas para este usuario en esta empresa (se suman al rol base)."
    )

    class Meta:
        # Un usuario solo puede tener UN rol principal por empresa
        unique_together = ('usuario', 'empresa')
        verbose_name = "Asignación de Rol"
        verbose_name_plural = "Asignaciones de Roles"

    def __str__(self):
        return f"{self.usuario.username} -> {self.empresa.codigo} [{self.grupo.name}]"


# ==============================================================================
# 6. AUDITORÍA DE SEGURIDAD
# ==============================================================================
class HistorialCambiosRol(models.Model):
    """
    Log inmutable de cambios críticos en permisos.
    Permite responder: "¿Quién le dio permiso de admin a Juan Pérez el martes?"
    """
    fecha = models.DateTimeField(auto_now_add=True)
    actor = models.ForeignKey(User, related_name='auditoria_actor', on_delete=models.PROTECT)
    usuario_afectado = models.ForeignKey(User, related_name='auditoria_afectado', on_delete=models.PROTECT)
    accion = models.CharField(max_length=255) # Ej: "Delegación Temporal", "Revocación"
    detalle = models.TextField()
    
    def __str__(self):
        return f"{self.fecha} - {self.actor} modificó a {self.usuario_afectado}"


# ==============================================================================
# 7. PERFIL DE SEGURIDAD (EXTENSIÓN DE USUARIO)
# ==============================================================================
class PerfilUsuario(models.Model):
    """
    Extiende el usuario nativo para almacenar banderas de seguridad.
    Se usa principalmente para forzar el cambio de contraseña al primer inicio.
    """
    usuario = models.OneToOneField(User, on_delete=models.CASCADE, related_name='perfil_usuario')
    
    debe_cambiar_password = models.BooleanField(
        default=True, 
        help_text="Si es True, el frontend bloqueará el acceso al Dashboard hasta que cambie la clave."
    )

    def __str__(self):
        return f"{self.usuario.username} - Cambio Pendiente: {self.debe_cambiar_password}"


# ==============================================================================
# 8. AUTOMATIZACIÓN (SEÑALES)
# ==============================================================================
@receiver(post_save, sender=User)
def crear_perfil_usuario(sender, instance, created, **kwargs):
    """
    Signal: Se dispara automáticamente cada vez que se crea un User.
    Garantiza que todo usuario nuevo nazca con un PerfilUsuario asociado.
    """
    if created:
        PerfilUsuario.objects.create(usuario=instance)
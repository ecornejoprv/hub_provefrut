"""
CORE ADMIN - CONFIGURACIÓN DEL PANEL DE ADMINISTRACIÓN
------------------------------------------------------
Este archivo define cómo se visualizan y gestionan los modelos en el panel (/admin).

ESTRATEGIA DE DISEÑO:
1. Inlines: Extendemos los modelos nativos (User, Group) inyectando nuestros 
   modelos de perfil (PerfilUsuario, PerfilGrupo) dentro de ellos.
2. Auditoría: El historial es estrictamente de solo lectura para garantizar integridad.
3. Usabilidad: Uso de 'filter_horizontal' y 'autocomplete_fields' para manejar 
   grandes volúmenes de usuarios y permisos sin trabar la interfaz.
"""

from django.contrib import admin
# Importamos los Admins base para poder extenderlos
from django.contrib.auth.admin import GroupAdmin as BaseGroupAdmin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import Group, User

from .models import (
    Empresa, 
    Pertenencia, 
    Area, 
    PerfilGrupo, 
    HistorialCambiosRol, 
    PerfilUsuario
)


# ==============================================================================
# 1. ESTRUCTURA ORGANIZACIONAL
# ==============================================================================
@admin.register(Area)
class AreaAdmin(admin.ModelAdmin):
    """
    Gestión de Departamentos/Áreas.
    Simple y directo.
    """
    list_display = ('nombre', 'codigo')
    search_fields = ('nombre', 'codigo')


# ==============================================================================
# 2. EXTENSIÓN DE GRUPOS (ROLES CON CONTEXTO)
# ==============================================================================
# Definimos el bloque que se incrustará dentro del Grupo nativo
class PerfilGrupoInline(admin.StackedInline):
    model = PerfilGrupo
    can_delete = False
    verbose_name_plural = 'Configuración de Área y Rol'
    # Texto de ayuda para el administrador
    help_text = "Asocie este Grupo a un Área funcional (ej: Logística)."

# Des-registramos el Grupo original y lo reemplazamos con nuestra versión mejorada
admin.site.unregister(Group)

@admin.register(Group)
class GroupAdmin(BaseGroupAdmin):
    """
    Admin de Grupos enriquecido.
    Muestra a qué área pertenece cada rol directamente en la lista.
    """
    inlines = (PerfilGrupoInline,)
    list_display = ('name', 'get_area')

    def get_area(self, obj):
        # Navegamos la relación inversa de forma segura
        return obj.perfil.area.nombre if hasattr(obj, 'perfil') else '-'
    get_area.short_description = 'Área / Departamento'


# ==============================================================================
# 3. ENTIDADES (EMPRESAS)
# ==============================================================================
@admin.register(Empresa)
class EmpresaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'codigo', 'activo')
    search_fields = ('nombre', 'codigo')
    list_filter = ('activo',)


# ==============================================================================
# 4. MATRIZ DE PERTENENCIA (CORE DEL HUB)
# ==============================================================================
@admin.register(Pertenencia)
class PertenenciaAdmin(admin.ModelAdmin):
    """
    Panel central de asignación de accesos.
    Aquí se define: Quién (Usuario) -> Qué es (Rol) -> Dónde (Empresa).
    """
    list_display = ('usuario', 'empresa', 'grupo', 'area')
    list_filter = ('empresa', 'grupo', 'area')
    
    # Búsqueda optimizada para cuando tengas miles de usuarios
    search_fields = ('usuario__username', 'usuario__email', 'usuario__first_name')
    
    # Autocomplete: Vital para no cargar un dropdown con 5000 usuarios
    autocomplete_fields = ('usuario', 'grupo', 'empresa')
    
    # Interfaz de doble caja para seleccionar múltiples permisos visualmente
    filter_horizontal = ('permisos_adicionales',)
    
    fieldsets = (
        ('Identidad', {
            'fields': ('usuario', 'empresa')
        }),
        ('Rol Base', {
            'fields': ('grupo', 'area'),
            'description': 'El rol define los permisos estándar del cargo.'
        }),
        ('Excepciones', {
            'fields': ('permisos_adicionales',),
            'description': 'Permisos extra granulares solo para este usuario en esta empresa.'
        }),
    )


# ==============================================================================
# 5. AUDITORÍA Y SEGURIDAD
# ==============================================================================
@admin.register(HistorialCambiosRol)
class HistorialAdmin(admin.ModelAdmin):
    """
    Log de auditoría inmutable.
    Nadie puede agregar o borrar registros manualmente desde aquí.
    """
    list_display = ('fecha', 'actor', 'usuario_afectado', 'accion')
    list_filter = ('accion', 'fecha')
    search_fields = ('actor__username', 'usuario_afectado__username', 'detalle')
    
    # Todos los campos son de solo lectura para preservar la evidencia
    readonly_fields = ('fecha', 'actor', 'usuario_afectado', 'accion', 'detalle')
    
    def has_add_permission(self, request):
        return False  # Bloquea el botón "Agregar"

    def has_delete_permission(self, request, obj=None):
        return False  # Bloquea el botón "Borrar"


# ==============================================================================
# 6. CONFIGURACIÓN DE USUARIOS (CON PERFIL DE SEGURIDAD)
# ==============================================================================

# El bloque que inyecta la bandera "Debe cambiar contraseña"
class PerfilUsuarioInline(admin.StackedInline):
    model = PerfilUsuario
    can_delete = False
    verbose_name_plural = 'Perfil de Seguridad (Cambio de Clave)'
    fk_name = 'usuario'

# Reemplazo del Admin de Usuario nativo
class UserAdmin(BaseUserAdmin):
    inlines = (PerfilUsuarioInline,)

    # Agregamos la columna de estado a la lista general
    list_display = BaseUserAdmin.list_display + ('debe_cambiar_password_status',)

    def debe_cambiar_password_status(self, obj):
        return obj.perfil_usuario.debe_cambiar_password if hasattr(obj, 'perfil_usuario') else False
    
    # Decoradores para que se vea bonito en el admin (Check verde/rojo)
    debe_cambiar_password_status.boolean = True 
    debe_cambiar_password_status.short_description = "Cambio Pendiente"

# Aplicamos el cambio
admin.site.unregister(User)
admin.site.register(User, UserAdmin)
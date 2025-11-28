from django.contrib import admin
from django.contrib.auth.admin import GroupAdmin as BaseGroupAdmin
from django.contrib.auth.models import Group

from .models import Empresa, Pertenencia, Area, PerfilGrupo, HistorialCambiosRol

# 1. Configuración de Áreas
@admin.register(Area)
class AreaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'codigo')
    search_fields = ('nombre',)

# 2. Mejorar el Admin de GRUPOS para incluir el Área
# Creamos un "Inline" para que el Área aparezca dentro del Grupo
class PerfilGrupoInline(admin.StackedInline):
    model = PerfilGrupo
    can_delete = False
    verbose_name_plural = 'Configuración de Área y Rol'

# Des-registramos el Grupo original y lo registramos con nuestra mejora
admin.site.unregister(Group)
@admin.register(Group)
class GroupAdmin(BaseGroupAdmin):
    inlines = (PerfilGrupoInline,)
    list_display = ('name', 'get_area')

    def get_area(self, obj):
        return obj.perfil.area.nombre if hasattr(obj, 'perfil') else '-'
    get_area.short_description = 'Área / Departamento'

# 3. Configuración de Empresas
@admin.register(Empresa)
class EmpresaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'codigo', 'activo')
    search_fields = ('nombre', 'codigo')

# 4. Configuración de Pertenencias (La Matriz)
@admin.register(Pertenencia)
class PertenenciaAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'empresa', 'grupo', 'area')
    list_filter = ('empresa', 'grupo', 'area')
    search_fields = ('usuario__username', 'usuario__email')
    autocomplete_fields = ('usuario', 'grupo', 'empresa')
    
    # Para ver los permisos adicionales de forma bonita
    filter_horizontal = ('permisos_adicionales',)

# 5. Auditoría (Solo lectura)
@admin.register(HistorialCambiosRol)
class HistorialAdmin(admin.ModelAdmin):
    list_display = ('fecha', 'actor', 'usuario_afectado', 'accion')
    readonly_fields = ('fecha', 'actor', 'usuario_afectado', 'accion', 'detalle')
    
    def has_add_permission(self, request):
        return False # Nadie puede crear logs falsos manualmente
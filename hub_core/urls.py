from django.contrib import admin
from django.urls import path
from core.views import CustomLoginView, SelectEmpresaView, DelegarPermisosView

# Importaciones de Swagger
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Endpoint 1: Login Inicial (Dame usuario/clave -> Te doy token básico + empresas)
    path('api/login/', CustomLoginView.as_view(), name='login'),
    
    # Endpoint 2: Selección (Dame empresa_id -> Te doy Pasaporte Universal)
    path('api/select-empresa/', SelectEmpresaView.as_view(), name='select_empresa'),

    #Endpoint 3: Delegar Permisos (Dame usuario_id, permisos -> Actualizo permisos)
    path('api/delegar-permiso/', DelegarPermisosView.as_view(), name='delegar_permiso'),

    # --- DOCUMENTACIÓN SWAGGER ---
    # 1. El archivo crudo (YAML) que usan las máquinas
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    
    # 2. La Interfaz Gráfica bonita para humanos
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
]
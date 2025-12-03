"""
HUB CORE URLS - ENRUTAMIENTO PRINCIPAL
--------------------------------------
Este archivo define el mapa de carreteras de la API.

ESTRUCTURA DE ENDPOINTS:
1. Administración: Panel nativo de Django.
2. Autenticación: Login y selección de contexto (Empresa).
3. Seguridad: Recuperación de cuentas y cambio obligatorio de clave.
4. Gestión: Delegación de permisos por jefaturas.
5. Documentación: Especificación OpenAPI (Swagger) para desarrolladores externos.
"""

from django.contrib import admin
from django.urls import path

# Importamos las vistas del núcleo de negocio
from core.views import (
    CustomLoginView, 
    SelectEmpresaView, 
    DelegarPermisosView, 
    PasswordResetRequestView, 
    PasswordResetConfirmView,
    CambiarPasswordPropioView
)

# Herramientas de documentación automática
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView


urlpatterns = [
    # ==========================================================================
    # 1. ADMINISTRACIÓN DEL SISTEMA
    # ==========================================================================
    path('admin/', admin.site.urls),
    

    # ==========================================================================
    # 2. AUTENTICACIÓN Y CONTEXTO (EL PASAPORTE)
    # ==========================================================================
    # Paso A: Login básico (User/Pass) -> Devuelve Token Temporal
    path('api/login/', CustomLoginView.as_view(), name='login'),
    
    # Paso B: Selección de Empresa -> Devuelve Token Final (Con Permisos)
    path('api/select-empresa/', SelectEmpresaView.as_view(), name='select_empresa'),


    # ==========================================================================
    # 3. SEGURIDAD Y RECUPERACIÓN DE CUENTAS
    # ==========================================================================
    # Flujo de "Olvidé mi contraseña" (Público)
    path('api/password-reset/', PasswordResetRequestView.as_view(), name='password_reset_request'),
    path('api/password-reset-confirm/', PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    
    # Flujo de "Cambio Forzado" (Usuario logueado por primera vez)
    path('api/cambiar-password-obligatorio/', CambiarPasswordPropioView.as_view(), name='change_password_mandatory'),


    # ==========================================================================
    # 4. GESTIÓN OPERATIVA (JEFATURAS)
    # ==========================================================================
    # Permite a un Gerente dar permisos temporales a sus subordinados
    path('api/delegar-permiso/', DelegarPermisosView.as_view(), name='delegar_permiso'),


    # ==========================================================================
    # 5. DOCUMENTACIÓN TÉCNICA (SWAGGER / OPENAPI)
    # ==========================================================================
    # El esquema crudo (YAML) para máquinas o generadores de código
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    
    # La interfaz gráfica interactiva para probar la API
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
]
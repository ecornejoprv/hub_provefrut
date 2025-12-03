"""
Django settings for Hub de Identidad Provefrut.

ARQUITECTURA:
- Backend: Django Rest Framework (API pura)
- Frontend: React / Vite (Desacoplado)
- Despliegue: Docker Container (App Runner / ECS)
- Base de Datos: PostgreSQL Externo (RDS)
- Archivos Estáticos: Whitenoise (Self-contained)

Este archivo está optimizado para leer configuración estrictamente
desde variables de entorno (.env), cumpliendo con los estándares
de seguridad 12-Factor App.
"""

from pathlib import Path
import os
from datetime import timedelta
from dotenv import load_dotenv 

# ==============================================================================
# 1. CARGA DE ENTORNO
# ==============================================================================
# Construimos rutas dentro del proyecto: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Cargamos las variables de entorno desde el archivo .env si existe.
# Esto es vital para el desarrollo local. En AWS, las variables se inyectan
# directamente en el entorno del contenedor.
env_path = BASE_DIR / '.env'
load_dotenv(dotenv_path=env_path)


# ==============================================================================
# 2. SEGURIDAD CRÍTICA
# ==============================================================================
# ADVERTENCIA: La SECRET_KEY es la llave maestra de la criptografía de Django.
# Si no está presente, fallamos rápido para evitar arrancar inseguros.
SECRET_KEY = os.getenv('SECRET_KEY')
if not SECRET_KEY:
    raise ValueError("FATAL: Falta la variable de entorno SECRET_KEY.")

# DEBUG: Debe ser False en producción para evitar filtrar datos sensibles en errores.
DEBUG = os.getenv('DEBUG', 'False') == 'True'

# ALLOWED_HOSTS: Lista blanca de dominios/IPs que pueden servir esta app.
# En producción, esto debe incluir el dominio de App Runner/Load Balancer.
ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', 'localhost').split(',')


# ==============================================================================
# 3. APLICACIONES INSTALADAS
# ==============================================================================
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # --- LIBRERÍAS DE TERCEROS ---
    'rest_framework',           # Motor de API
    'rest_framework_simplejwt', # Autenticación JWT
    'corsheaders',              # Permite que React (otro dominio) hable con Django
    'drf_spectacular',          # Documentación automática (Swagger)

    # --- APLICACIONES DE NEGOCIO (PROPIAS) ---
    'core',                     # Lógica principal del Hub
]


# ==============================================================================
# 4. MIDDLEWARE (La tubería de procesamiento)
# ==============================================================================
MIDDLEWARE = [
    # CORS debe ser lo primero: si el origen no es válido, rechazamos antes de procesar nada.
    'corsheaders.middleware.CorsMiddleware',
    
    'django.middleware.security.SecurityMiddleware',
    
    # WHITENOISE: Sirve archivos estáticos (CSS/JS) directamente desde Python.
    # Vital para Docker y AWS App Runner donde no hay un Nginx dedicado a estáticos.
    'whitenoise.middleware.WhiteNoiseMiddleware',
    
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'hub_core.urls'


# ==============================================================================
# 5. TEMPLATES
# ==============================================================================
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'hub_core.wsgi.application'


# ==============================================================================
# 6. BASE DE DATOS
# ==============================================================================
# Configuración agnóstica. Funciona igual en Local (Docker) y Producción (RDS).
# Solo cambian las variables de entorno.
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('DB_NAME'),
        'USER': os.getenv('DB_USER'),
        'PASSWORD': os.getenv('DB_PASSWORD'),
        'HOST': os.getenv('DB_HOST'),
        'PORT': os.getenv('DB_PORT', '5432'),
    }
}


# ==============================================================================
# 7. VALIDACIÓN DE CONTRASEÑAS
# ==============================================================================
AUTH_PASSWORD_VALIDATORS = [
    { 'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator', },
    { 'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator', },
    { 'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator', },
    { 'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator', },
]


# ==============================================================================
# 8. INTERNACIONALIZACIÓN
# ==============================================================================
LANGUAGE_CODE = 'es-ec'        # Español Ecuador
TIME_ZONE = 'America/Guayaquil' # Zona Horaria del servidor
USE_I18N = True
USE_TZ = True


# ==============================================================================
# 9. ARCHIVOS ESTÁTICOS (WHITENOISE)
# ==============================================================================
STATIC_URL = '/static/'

# STATIC_ROOT: Es la carpeta donde 'collectstatic' reunirá todos los archivos.
# Usamos 'static' (singular) para coincidir con la configuración de Nginx.
STATIC_ROOT = BASE_DIR / 'static'

# Motor de almacenamiento optimizado (Gzip/Brotli + Cacheo)
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'


# ==============================================================================
# 10. SEGURIDAD DE ORIGEN (CORS & CSRF)
# ==============================================================================
# Define qué dominios de Frontend (React) tienen permiso para hablar con la API.
# Esto previene ataques desde sitios maliciosos.

# Lista de orígenes confiables (ej: http://localhost:5173, https://hub.provefrut.com)
cors_origins_raw = os.getenv('CORS_ALLOWED_ORIGINS', 'http://localhost:5173')
CORS_ALLOWED_ORIGINS = cors_origins_raw.split(',')

# Para cookies seguras y POST requests
csrf_origins_raw = os.getenv('CSRF_TRUSTED_ORIGINS', 'http://localhost:5173')
CSRF_TRUSTED_ORIGINS = csrf_origins_raw.split(',')


# ==============================================================================
# 11. REST FRAMEWORK & DOCUMENTACIÓN
# ==============================================================================
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
    
    # --- RATE LIMITING (Ajustado para Oficina Corporativa) ---
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle'
    ],
    'DEFAULT_THROTTLE_RATES': {
        # 100 intentos por minuto por IP.
        # Permite que toda la oficina entre a las 8:00 AM sin bloquearse,
        # pero detiene scripts agresivos que intenten miles de claves.
        'anon': '100/minute', 
        
        # 2000 peticiones al día por usuario logueado.
        # Suficiente para un uso intensivo del sistema.
        'user': '2000/day'    
    }
}

SPECTACULAR_SETTINGS = {
    'TITLE': 'Hub de Identidad Provefrut API',
    'DESCRIPTION': 'Sistema centralizado de autenticación y autorización Multi-Empresa.',
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
    'COMPONENT_SPLIT_REQUEST': True,
}


# ==============================================================================
# 12. JWT CONFIGURACIÓN (TOKENS)
# ==============================================================================
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(hours=8),  # Duración de la sesión laboral
    'REFRESH_TOKEN_LIFETIME': timedelta(days=1),
    'SIGNING_KEY': SECRET_KEY, 
    'ALGORITHM': 'HS256',
    'AUTH_HEADER_TYPES': ('Bearer',),
}


# ==============================================================================
# 13. CONFIGURACIÓN DE CORREO (SMTP)
# ==============================================================================
# Usamos el backend SMTP real para producción y pruebas locales conectadas.
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'

# Configuración del servidor (Office 365, Gmail, AWS SES)
EMAIL_HOST = os.getenv('EMAIL_HOST')
EMAIL_PORT = int(os.getenv('EMAIL_PORT', 587))
EMAIL_USE_TLS = os.getenv('EMAIL_USE_TLS', 'True') == 'True'
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD')

# Remitente por defecto para correos automáticos
DEFAULT_FROM_EMAIL = os.getenv('DEFAULT_FROM_EMAIL', EMAIL_HOST_USER)

# URL del Frontend para generar links (ej: Reset Password)
# En local es http://172.20...:5173, en Prod será el dominio HTTPS real.
FRONTEND_URL = os.getenv('FRONTEND_URL', 'http://localhost')


# ==============================================================================
# 14. SISTEMA
# ==============================================================================
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ==========================================
# CONFIGURACIÓN PARA PROXY REVERSO (AWS/NGINX)
# ==========================================
# Esto permite que Django sepa que está detrás de un HTTPS seguro (AWS Load Balancer)
# y genere links https:// en lugar de http://
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
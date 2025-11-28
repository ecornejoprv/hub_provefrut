"""
Django settings for hub_core project.
Optimized for Docker, Cloud Deployment (AWS), and Local Development.
"""

from pathlib import Path
import os
from datetime import timedelta
from dotenv import load_dotenv 

# 1. CARGA DE ENTORNO
# ------------------------------------------------------------------------------
# Carga variables desde el archivo .env si existe (Desarrollo Local).
# En producción (AWS App Runner/Lambda), las variables se inyectan por sistema.
load_dotenv()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# 2. SEGURIDAD CRÍTICA
# ------------------------------------------------------------------------------
# ADVERTENCIA: Si SECRET_KEY falta, el sistema debe fallar inmediatamente.
SECRET_KEY = os.getenv('SECRET_KEY')
if not SECRET_KEY:
    raise ValueError("Falta la variable de entorno SECRET_KEY. El sistema no puede iniciar.")

# DEBUG: Por defecto es False para seguridad. Solo es True si el .env lo dice explícitamente.
DEBUG = os.getenv('DEBUG', 'False') == 'True'

# HOSTS: Lista de IPs/Dominios permitidos.
ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', 'localhost').split(',')


# 3. APLICACIONES INSTALADAS
# ------------------------------------------------------------------------------
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Librerías de Terceros
    'rest_framework',
    'rest_framework_simplejwt', # Asegúrate de que esta esté instalada
    'corsheaders',
    'drf_spectacular',

    # Mis Aplicaciones (Módulos de Negocio)
    'core',
]

# 4. MIDDLEWARE (Procesadores de Peticiones)
# ------------------------------------------------------------------------------
MIDDLEWARE = [
    # CORS: Debe ir lo más arriba posible para validar el origen antes que nada.
    'corsheaders.middleware.CorsMiddleware',
    
    'django.middleware.security.SecurityMiddleware',
    
    # WHITENOISE: Sirve archivos estáticos (CSS/JS) en Docker/Producción de forma eficiente.
    'whitenoise.middleware.WhiteNoiseMiddleware', 
    
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'hub_core.urls'

# 5. TEMPLATES
# ------------------------------------------------------------------------------
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


# 6. BASE DE DATOS
# ------------------------------------------------------------------------------
# Leemos estrictamente de variables de entorno.
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('DB_NAME'),
        'USER': os.getenv('DB_USER'),
        'PASSWORD': os.getenv('DB_PASSWORD'),
        'HOST': os.getenv('DB_HOST'),
        'PORT': os.getenv('DB_PORT'),
    }
}


# 7. VALIDACIÓN DE CONTRASEÑAS
# ------------------------------------------------------------------------------
AUTH_PASSWORD_VALIDATORS = [
    { 'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator', },
    { 'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator', },
    { 'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator', },
    { 'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator', },
]


# 8. INTERNACIONALIZACIÓN
# ------------------------------------------------------------------------------
LANGUAGE_CODE = 'es-ec' # Ajustado a Ecuador/Español
TIME_ZONE = 'America/Guayaquil' # Ajustado a tu zona horaria real
USE_I18N = True
USE_TZ = True


# 9. ARCHIVOS ESTÁTICOS (Vital para Docker/Nginx/AWS)
# ------------------------------------------------------------------------------
STATIC_URL = 'static/'
# Carpeta donde collectstatic reunirá todo (CSS admin, Swagger, etc.)
STATIC_ROOT = BASE_DIR / 'staticfiles' 

# Configuración de Whitenoise para servir estáticos optimizados
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'


# 10. SEGURIDAD DE ORIGEN (CORS & CSRF)
# ------------------------------------------------------------------------------
# Define quién puede hablar con la API (React Frontend)
CORS_ALLOWED_ORIGINS = os.getenv('CORS_ALLOWED_ORIGINS', 'http://localhost:5173').split(',')
CSRF_TRUSTED_ORIGINS = os.getenv('CSRF_TRUSTED_ORIGINS', 'http://localhost:5173').split(',')

# 11. REST FRAMEWORK & DOCUMENTACIÓN
# ------------------------------------------------------------------------------
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
}

SPECTACULAR_SETTINGS = {
    'TITLE': 'Hub de Identidad Provefrut API',
    'DESCRIPTION': 'Sistema centralizado de autenticación y autorización Multi-Empresa.',
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
    'COMPONENT_SPLIT_REQUEST': True,
}

# 12. JWT CONFIGURACIÓN (Simple JWT)
# ------------------------------------------------------------------------------
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(hours=8),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=1),
    'SIGNING_KEY': SECRET_KEY, 
    'ALGORITHM': 'HS256',
    'AUTH_HEADER_TYPES': ('Bearer',),
}

# 13. ID DEL CAMPO PRIMARIO POR DEFECTO
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
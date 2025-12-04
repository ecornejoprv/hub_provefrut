#!/bin/sh

# Detener si hay error
set -e

echo "🚀 [BACKEND] Iniciando Entrypoint..."

# 1. Migraciones (Base de datos)
echo "📦 Aplicando migraciones a la Base de Datos..."
python manage.py migrate

# 2. Estáticos (Whitenoise)
echo "🎨 Recolectando archivos estáticos (CSS/JS)..."
# Esto generará la carpeta /app/static dentro del contenedor
python manage.py collectstatic --noinput

# 3. Iniciar Servidor (Gunicorn)
echo "🔥 Iniciando Gunicorn en puerto 8000..."
exec python3 -m gunicorn hub_core.wsgi:application --bind 0.0.0.0:8000
#!/bin/sh

# Detener si hay error
set -e

echo "🚀 [BACKEND] Iniciando Entrypoint..."

# 1. Migraciones (Usando ruta directa del venv)
echo "📦 Aplicando migraciones..."
./venv/bin/python3 manage.py migrate

# 2. Estáticos
echo "🎨 Recolectando estáticos..."
./venv/bin/python3 manage.py collectstatic --noinput

# 3. Iniciar Servidor
echo "🔥 Iniciando Gunicorn..."
# IMPORTANTE: Usar exec y la ruta completa
exec ./venv/bin/python3 -m gunicorn hub_core.wsgi:application --bind 0.0.0.0:8000
# 1. Imagen Base (Linux Python)
FROM python:3.11-slim

# 2. Optimizaciones de Python
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# 3. Directorio de trabajo
WORKDIR /app

# 4. Dependencias del Sistema (Para Postgres y compilación)
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    netcat-openbsd \
    && rm -rf /var/lib/apt/lists/*

# 5. Dependencias de Python
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt
# Instalamos Gunicorn y Whitenoise explícitamente por si faltan en requirements
RUN pip install gunicorn whitenoise

# 6. Copiar Código
COPY . /app/

# 7. Configurar Entrypoint (Solución para Windows CRLF)
COPY ./entrypoint.sh /app/entrypoint.sh
RUN sed -i 's/\r$//g' /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

# 8. Puerto Interno
EXPOSE 8000

# 9. Ejecutar
ENTRYPOINT ["/app/entrypoint.sh"]
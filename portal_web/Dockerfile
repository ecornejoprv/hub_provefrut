# ETAPA 1: Construcción (Node.js)
FROM node:22-alpine as build

WORKDIR /app

# Instalar dependencias (aprovechando caché)
COPY package.json package-lock.json ./
RUN npm install

# Copiar código fuente
COPY . .

# Argumentos de construcción (Variables de entorno para el Build)
# Esto permite inyectar las URLs de los otros sistemas
ARG VITE_URL_COMPRAS
ARG VITE_URL_CHATBOT
ENV VITE_URL_COMPRAS=$VITE_URL_COMPRAS
ENV VITE_URL_CHATBOT=$VITE_URL_CHATBOT

# Compilar (Genera carpeta /dist)
RUN npm run build

# ETAPA 2: Servidor (Nginx)
FROM nginx:alpine

# Copiar archivos compilados
COPY --from=build /app/dist /usr/share/nginx/html

# Copiar configuración de Nginx
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
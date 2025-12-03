# Hub de Identidad Provefrut

Sistema centralizado de autenticación y autorización (Identity Provider) multi-empresa.

## 🏗 Arquitectura

El sistema está desacoplado en dos servicios contenerizados:

* **Backend:** Django Rest Framework (Python 3.11). Expone API REST y Panel Admin.
* **Frontend:** React + Vite (Node 18). SPA servida mediante Nginx.
* **Base de Datos:** PostgreSQL (Externa/RDS).

## 🚀 Despliegue Local (Docker)

Para levantar el entorno de producción localmente (simulando AWS):

1.  **Configurar Entorno:**
    Copiar `.env.example` a `.env` y configurar las credenciales de BD y correos.
    *(Solicitar credenciales al equipo de desarrollo)*.

2.  **Ejecutar:**
    ```bash
    docker-compose -f docker-compose.prod.yml up --build -d
    ```

3.  **Accesos:**
    * **Frontend (App):** http://localhost:8080
    * **Backend (Admin):** http://localhost:8080/admin/
    * **API Docs:** http://localhost:8080/api/docs/

## ☁️ Guía de Despliegue AWS (Para Consultores)

El proyecto está preparado para **AWS App Runner** (Backend) y **AWS Amplify** (Frontend), o una arquitectura de contenedores estándar (ECS).

### Requisitos de Backend (Variables de Entorno)
Configurar en el servicio de computación (App Runner/ECS/Lambda):

* `SECRET_KEY`: Generar una cadena segura.
* `DEBUG`: `False` (Obligatorio).
* `ALLOWED_HOSTS`: Dominio del backend (ej: `api.hub.provefrut.com`).
* `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT`: Credenciales RDS.
* `CORS_ALLOWED_ORIGINS`: Dominio del frontend (ej: `https://hub.provefrut.com`).
* `CSRF_TRUSTED_ORIGINS`: Dominio del frontend.
* `FRONTEND_URL`: URL base del frontend (para generación de links de correos).
* `EMAIL_...`: Credenciales SMTP (SES o Outlook).

### Requisitos de Frontend (Build Time)
Configurar en el servicio de Build (Amplify/CodeBuild):

* `VITE_URL_COMPRAS`: URL del módulo de compras.
* `VITE_URL_CHATBOT`: URL del chatbot.
* **Nota:** La API Base URL es relativa (`/api/`) para soportar Reverse Proxy, o debe configurarse si se usan dominios separados.

## 📦 Estructura del Proyecto

* `/hub_provefrut`: Código fuente Django.
* `/portal_web`: Código fuente React.
* `docker-compose.prod.yml`: Orquestación para producción local.
"""
CORE VIEWS - CONTROLADORES DE LA API
------------------------------------
Este módulo contiene la lógica de negocio expuesta a través de endpoints REST.

ESTRUCTURA:
1. Autenticación Inicial (Login extendido).
2. Gestión de Identidad (Selección de Empresa / Contexto).
3. Administración Delegada (Gerentes asignando permisos).
4. Seguridad y Recuperación (Reset Password / Cambio Obligatorio).
"""

from django.shortcuts import get_object_or_404
from django.contrib.auth.models import Permission, User
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.core.mail import send_mail
from django.conf import settings

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from .models import Pertenencia, Empresa, HistorialCambiosRol
from .serializers import (
    EmpresaSerializer, 
    PasswordResetRequestSerializer, 
    PasswordResetConfirmSerializer
)


# ==============================================================================
# 1. AUTENTICACIÓN INICIAL (LOGIN)
# ==============================================================================

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    Extiende el Login estándar de JWT para devolver información de contexto
    adicional (Empresas disponibles, alertas de seguridad) junto con el token.
    """
    def validate(self, attrs):
        # Validación estándar (Usuario/Password)
        data = super().validate(attrs)
        
        # --- SEGURIDAD: CHECK DE CAMBIO OBLIGATORIO ---
        debe_cambiar = False
        if hasattr(self.user, 'perfil_usuario'):
            debe_cambiar = self.user.perfil_usuario.debe_cambiar_password
        
        data['debe_cambiar_password'] = debe_cambiar

        # --- CONTEXTO: EMPRESAS DISPONIBLES ---
        pertenencias = Pertenencia.objects.filter(usuario=self.user)
        empresas = [p.empresa for p in pertenencias]
        data['empresas_disponibles'] = EmpresaSerializer(empresas, many=True).data
        
        return data

class CustomLoginView(TokenObtainPairView):
    """
    Endpoint: POST /api/login/
    Punto de entrada principal. Devuelve credenciales temporales y contexto.
    """
    serializer_class = CustomTokenObtainPairSerializer


# ==============================================================================
# 2. GESTIÓN DE IDENTIDAD (EL PASAPORTE)
# ==============================================================================

class SelectEmpresaView(APIView):
    """
    Endpoint: POST /api/select-empresa/
    Generador del 'Pasaporte Universal'.
    
    Recibe: ID de Empresa + Token Temporal (Auth Header).
    Devuelve: Token JWT Final con todos los permisos cargados para esa empresa.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        empresa_id = request.data.get('empresa_id')
        
        if not empresa_id:
            return Response({"error": "Falta el campo 'empresa_id'"}, status=400)

        # Validación de Seguridad: ¿El usuario realmente pertenece a esa empresa?
        try:
            pertenencia = Pertenencia.objects.get(
                usuario=request.user, 
                empresa_id=empresa_id
            )
        except Pertenencia.DoesNotExist:
            return Response({"error": "No tienes acceso a esta empresa"}, status=403)

        # Construcción del Token Enriquecido
        token = AccessToken.for_user(request.user)

        # Inyectar Contexto (Dónde estoy)
        token['empresa_id'] = pertenencia.empresa.id
        token['empresa_codigo'] = pertenencia.empresa.codigo
        token['empresa_nombre'] = pertenencia.empresa.nombre
        token['rol_nombre'] = pertenencia.grupo.name

        # Inyectar Identidad (Quién soy)
        token['username'] = request.user.username
        token['email'] = request.user.email
        full_name = f"{request.user.first_name} {request.user.last_name}".strip()
        token['nombre_completo'] = full_name.title() if full_name else request.user.username
        
        # Inyectar Autoridad (Qué puedo hacer)
        # Sumamos permisos del Grupo + Permisos Individuales (Excepciones)
        permisos_grupo = pertenencia.grupo.permissions.all()
        permisos_extra = pertenencia.permisos_adicionales.all()
        todos_los_permisos = permisos_grupo | permisos_extra
        
        # Aplanar permisos a lista de strings "app.codename"
        lista_permisos = [
            f"{p.content_type.app_label}.{p.codename}" 
            for p in todos_los_permisos.distinct()
        ]
        token['permisos'] = lista_permisos

        return Response({
            'access_token': str(token),
            'mensaje': f"Bienvenido a {pertenencia.empresa.nombre}"
        })


# ==============================================================================
# 3. ADMINISTRACIÓN DELEGADA
# ==============================================================================

class DelegarPermisosView(APIView):
    """
    Endpoint: POST /api/delegar-permiso/
    Permite a un Gerente asignar permisos temporales a sus subordinados directos.
    Reglas:
    1. El actor debe ser Gerente.
    2. El objetivo debe estar en la misma Área.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        target_user_id = request.data.get('usuario_destino_id')
        permiso_codename = request.data.get('permiso_codename') 
        empresa_id = request.data.get('empresa_id')
        accion = request.data.get('accion') # 'add' o 'remove'

        if not all([target_user_id, permiso_codename, empresa_id, accion]):
             return Response({"error": "Faltan datos obligatorios"}, status=400)

        # 1. Validar al Jefe
        try:
            pertenencia_jefe = Pertenencia.objects.get(usuario=request.user, empresa_id=empresa_id)
        except Pertenencia.DoesNotExist:
            return Response({"error": "No tienes acceso a esta empresa"}, status=403)

        if not hasattr(pertenencia_jefe.grupo, 'perfil') or not pertenencia_jefe.grupo.perfil.es_gerencial:
            return Response({"error": "No tienes permisos gerenciales para delegar."}, status=403)

        # 2. Validar al Empleado y Territorio
        pertenencia_empleado = get_object_or_404(Pertenencia, usuario_id=target_user_id, empresa_id=empresa_id)
        
        if pertenencia_jefe.grupo.perfil.area != pertenencia_empleado.grupo.perfil.area:
            return Response({
                "error": "Conflicto de Área: Solo puedes gestionar personal de tu departamento."
            }, status=403)

        # 3. Ejecutar Acción
        try:
            permiso = Permission.objects.get(codename=permiso_codename)
            
            if accion == 'add':
                pertenencia_empleado.permisos_adicionales.add(permiso)
                log_msg = f"Permiso '{permiso_codename}' OTORGADO por {request.user.username}"
            elif accion == 'remove':
                pertenencia_empleado.permisos_adicionales.remove(permiso)
                log_msg = f"Permiso '{permiso_codename}' REVOCADO por {request.user.username}"
            else:
                return Response({"error": "Acción inválida"}, status=400)

            # 4. Auditoría Obligatoria
            HistorialCambiosRol.objects.create(
                actor=request.user,
                usuario_afectado=pertenencia_empleado.usuario,
                accion=f"Delegación ({accion})",
                detalle=f"{log_msg} en empresa {pertenencia_jefe.empresa.codigo}"
            )

            return Response({"mensaje": "Operación exitosa", "detalle": log_msg})

        except Permission.DoesNotExist:
            return Response({"error": f"El permiso '{permiso_codename}' no existe"}, status=404)


# ==============================================================================
# 4. SEGURIDAD Y RECUPERACIÓN DE CUENTAS
# ==============================================================================

class PasswordResetRequestView(APIView):
    """
    Endpoint: POST /api/password-reset/
    Paso 1: El usuario olvidó su clave. Envía un link al correo.
    """
    permission_classes = [] # Acceso anónimo permitido

    def post(self, request):
        serializer = PasswordResetRequestSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            try:
                # Usamos get() porque el correo debe ser único en el sistema
                user = User.objects.get(email=email)
                
                token = default_token_generator.make_token(user)
                uid = urlsafe_base64_encode(force_bytes(user.pk))
                
                # Link apunta al Frontend (React)
                link = f"{settings.FRONTEND_URL}/reset-password/{uid}/{token}"
                
                send_mail(
                    subject='Restablecer Contraseña - Hub Provefrut',
                    message=f'Hola {user.username}.\n\nUsa este enlace para cambiar tu clave:\n{link}\n\nSi no fuiste tú, ignora este mensaje.',
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[email],
                    fail_silently=False,
                )
                
            except User.DoesNotExist:
                # Silent Fail: No revelamos si el correo existe o no
                pass 
            
            return Response({"mensaje": "Se han enviado instrucciones a tu correo."}, status=200)
        
        return Response(serializer.errors, status=400)


class PasswordResetConfirmView(APIView):
    """
    Endpoint: POST /api/password-reset-confirm/
    Paso 2: El usuario viene del link y establece su nueva clave.
    """
    permission_classes = [] 

    def post(self, request):
        serializer = PasswordResetConfirmSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            password = serializer.validated_data['password']
            
            user.set_password(password)
            user.save()
            
            return Response({"mensaje": "Contraseña actualizada. Inicia sesión."}, status=200)
        
        return Response(serializer.errors, status=400)


class CambiarPasswordPropioView(APIView):
    """
    Endpoint: POST /api/cambiar-password-obligatorio/
    Caso especial: Usuario logueado pero obligado a cambiar su clave inicial.
    """
    permission_classes = [IsAuthenticated] 

    def post(self, request):
        user = request.user
        password_nueva = request.data.get('password')
        
        if not password_nueva or len(password_nueva) < 8:
            return Response({"error": "La contraseña debe tener al menos 8 caracteres."}, status=400)

        # 1. Actualizar Password
        user.set_password(password_nueva)
        user.save()

        # 2. Desactivar la bandera de obligatoriedad
        if hasattr(user, 'perfil_usuario'):
            perfil = user.perfil_usuario
            perfil.debe_cambiar_password = False
            perfil.save()

        return Response({"mensaje": "Contraseña actualizada exitosamente."}, status=200)
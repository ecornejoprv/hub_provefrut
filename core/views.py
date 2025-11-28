# core/views.py

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from django.shortcuts import get_object_or_404
from django.contrib.auth.models import Permission, User
from .models import Pertenencia, Empresa, HistorialCambiosRol
from .serializers import EmpresaSerializer

# =============================================================================
# VISTA 1: LOGIN INICIAL (AJUSTADO)
# =============================================================================
# Esta vista intercepta el login normal para devolver, además del token temporal,
# la lista de empresas a las que el usuario tiene derecho de entrar.
class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        # 1. Validación estándar de Django (Usuario y Contraseña correctos)
        data = super().validate(attrs)
        
        # 2. Buscamos todas las "Pertenencias" de este usuario
        # (Es decir, en qué empresas está contratado/asignado)
        pertenencias = Pertenencia.objects.filter(usuario=self.user)
        
        # 3. Extraemos los objetos Empresa de esas pertenencias
        empresas = [p.empresa for p in pertenencias]
        
        # 4. Serializamos (convertimos a JSON) y adjuntamos a la respuesta
        data['empresas_disponibles'] = EmpresaSerializer(empresas, many=True).data
        
        return data

class CustomLoginView(TokenObtainPairView):
    """
    Endpoint: POST /api/login/
    """
    serializer_class = CustomTokenObtainPairSerializer


# =============================================================================
# VISTA 2: EL GENERADOR DE PASAPORTE UNIVERSAL (CORE DEL SISTEMA)
# =============================================================================
class SelectEmpresaView(APIView):
    """
    Endpoint: POST /api/select-empresa/
    Objetivo: Recibe una empresa ID y emite el Token Final (Pasaporte) 
    con todos los permisos cargados (Grupo + Excepciones).
    """
    permission_classes = [IsAuthenticated] # Requiere el token temporal del Login

    def post(self, request):
        # 1. Validar datos de entrada
        empresa_id = request.data.get('empresa_id')
        
        if not empresa_id:
            return Response({"error": "Falta el campo 'empresa_id'"}, status=400)

        try:
            # 2. SEGURIDAD CRÍTICA (Contexto)
            # Verificamos que el usuario tenga una fila en la tabla Pertenencia
            # para la empresa que está solicitando.
            pertenencia = Pertenencia.objects.get(
                usuario=request.user, 
                empresa_id=empresa_id
            )
        except Pertenencia.DoesNotExist:
            # Si no existe la fila, es un intento de hackeo o error. Bloqueamos.
            return Response({"error": "No tienes acceso a esta empresa"}, status=403)

        # 3. CREACIÓN DEL TOKEN (La Maleta Vacía)
        token = AccessToken.for_user(request.user)

        # ------------------------------------------------------------------
        # A. INYECCIÓN DE DATOS DE CONTEXTO (¿DÓNDE ESTOY?)
        # ------------------------------------------------------------------
        token['empresa_id'] = pertenencia.empresa.id
        token['empresa_codigo'] = pertenencia.empresa.codigo
        token['empresa_nombre'] = pertenencia.empresa.nombre
        token['rol_nombre'] = pertenencia.grupo.name # El nombre del cargo (ej. JEFE_BODEGA)

        # ------------------------------------------------------------------
        # B. INYECCIÓN DE DATOS DE IDENTIDAD (¿QUIÉN SOY?)
        # ------------------------------------------------------------------
        token['username'] = request.user.username
        token['email'] = request.user.email
        
        # Formateamos el nombre completo para que se vea bien en el Navbar
        full_name = f"{request.user.first_name} {request.user.last_name}".strip()
        token['nombre_completo'] = full_name.title() if full_name else request.user.username
        
        # ------------------------------------------------------------------
        # C. LÓGICA DE PERMISOS (CARGO + EXCEPCIONES) - ¡CORREGIDO!
        # ------------------------------------------------------------------
        # 1. Obtenemos los permisos estándar del Cargo (Grupo)
        permisos_grupo = pertenencia.grupo.permissions.all()
        
        # 2. Obtenemos los permisos "Bonus" asignados específicamente en esta Pertenencia
        # (Esto cubre las excepciones, ej: Jefe Bodega que ve Dispensario solo en esta empresa)
        permisos_extra = pertenencia.permisos_adicionales.all()
        
        # 3. Unimos ambos conjuntos usando el operador OR de QuerySets (|)
        # Esto suma los poderes sin duplicar objetos.
        todos_los_permisos = permisos_grupo | permisos_extra
        
        # 4. Aplanamos a una lista de texto para que React la entienda
        # Usamos .distinct() para asegurar que no haya duplicados si se solapan.
        lista_permisos = [
            f"{p.content_type.app_label}.{p.codename}" 
            for p in todos_los_permisos.distinct()
        ]
        
        token['permisos'] = lista_permisos # Guardamos la lista en el token

        # 5. Devolver el Pasaporte al Frontend
        return Response({
            'access_token': str(token),
            'mensaje': f"Bienvenido a {pertenencia.empresa.nombre}"
        })
    
class DelegarPermisosView(APIView):
    """
    Endpoint: POST /api/delegar-permiso/
    Permite a un GERENTE otorgar/quitar permisos temporales a sus SUBORDINADOS.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        # Datos del Body
        target_user_id = request.data.get('usuario_destino_id')
        permiso_codename = request.data.get('permiso_codename') 
        empresa_id = request.data.get('empresa_id')
        accion = request.data.get('accion') # 'add' o 'remove'

        if not all([target_user_id, permiso_codename, empresa_id, accion]):
             return Response({"error": "Faltan datos obligatorios"}, status=400)

        # 1. IDENTIFICAR AL JEFE (Actor)
        try:
            pertenencia_jefe = Pertenencia.objects.get(usuario=request.user, empresa_id=empresa_id)
        except Pertenencia.DoesNotExist:
            return Response({"error": "No tienes acceso a esta empresa"}, status=403)

        # 2. VERIFICAR RANGO (¿Es Gerente?)
        if not hasattr(pertenencia_jefe.grupo, 'perfil') or not pertenencia_jefe.grupo.perfil.es_gerencial:
            return Response({"error": "No tienes permisos gerenciales para delegar."}, status=403)

        # 3. IDENTIFICAR AL EMPLEADO (Destino)
        pertenencia_empleado = get_object_or_404(Pertenencia, usuario_id=target_user_id, empresa_id=empresa_id)

        # 4. VERIFICAR TERRITORIO (¿Están en la misma área?)
        area_jefe = pertenencia_jefe.grupo.perfil.area
        area_empleado = pertenencia_empleado.grupo.perfil.area
        
        # Validamos que el empleado sea de la misma área que el jefe
        if area_jefe != area_empleado:
            return Response({
                "error": f"Conflicto de Área: Tú eres de {area_jefe} y el usuario es de {area_empleado}."
            }, status=403)

        # 5. EJECUTAR ACCIÓN
        try:
            permiso = Permission.objects.get(codename=permiso_codename)
            
            if accion == 'add':
                pertenencia_empleado.permisos_adicionales.add(permiso)
                log_msg = f"Permiso '{permiso_codename}' OTORGADO por {request.user.username}"
            elif accion == 'remove':
                pertenencia_empleado.permisos_adicionales.remove(permiso)
                log_msg = f"Permiso '{permiso_codename}' REVOCADO por {request.user.username}"
            else:
                return Response({"error": "Acción inválida. Use 'add' o 'remove'"}, status=400)

            # 6. AUDITORÍA (Crucial para tu jefa)
            HistorialCambiosRol.objects.create(
                actor=request.user,
                usuario_afectado=pertenencia_empleado.usuario,
                accion=f"Delegación ({accion})",
                detalle=f"{log_msg} en empresa {pertenencia_jefe.empresa.codigo}"
            )

            return Response({"mensaje": "Operación exitosa", "detalle": log_msg})

        except Permission.DoesNotExist:
            return Response({"error": f"El permiso '{permiso_codename}' no existe en el sistema"}, status=404)
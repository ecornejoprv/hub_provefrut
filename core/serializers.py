"""
CORE SERIALIZERS - TRANSFORMACIÓN Y VALIDACIÓN DE DATOS
-------------------------------------------------------
Este módulo se encarga de:
1. Serializar modelos (Empresa, Pertenencia) a JSON para las respuestas de la API.
2. Validar datos de entrada para procesos críticos (Reset de Password).

ESTRATEGIA DE SEGURIDAD:
- Los campos sensibles (password) siempre son 'write_only'.
- Usamos decodificación Base64 para los IDs de usuario en URLs públicas para evitar
  problemas de codificación y ofuscación básica.
"""

from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_decode
from django.contrib.auth.models import User
from rest_framework import serializers

from .models import Empresa, Pertenencia


# ==============================================================================
# 1. SERIALIZADORES DE CONTEXTO (LOGIN Y DATOS BASE)
# ==============================================================================

class EmpresaSerializer(serializers.ModelSerializer):
    """
    Transforma el modelo Empresa a un JSON ligero.
    Se utiliza en el Login para mostrarle al usuario las empresas disponibles
    en el selector inicial.
    """
    class Meta:
        model = Empresa
        fields = ['id', 'nombre', 'codigo']


class UserContextSerializer(serializers.ModelSerializer):
    """
    Devuelve información enriquecida sobre la relación Usuario-Empresa.
    Útil para mostrar en el Dashboard "Quién soy y qué rol tengo aquí".
    """
    # Usamos 'source' para navegar a las relaciones (Foreign Keys)
    empresa_nombre = serializers.CharField(source='empresa.nombre')
    grupo_nombre = serializers.CharField(source='grupo.name')

    class Meta:
        model = Pertenencia
        fields = ['empresa_nombre', 'grupo_nombre']


# ==============================================================================
# 2. SERIALIZADORES DE SEGURIDAD (RESTABLECIMIENTO DE CONTRASEÑA)
# ==============================================================================

class PasswordResetRequestSerializer(serializers.Serializer):
    """
    Valida la solicitud inicial de restablecimiento.
    Recibe solo el email para minimizar la superficie de ataque.
    """
    email = serializers.EmailField()

    def validate_email(self, value):
        # NOTA DE SEGURIDAD: 
        # Aquí normalizamos el email (minúsculas) para evitar errores.
        # No validamos si el usuario existe o no para evitar "Enumeración de Usuarios"
        # por parte de atacantes.
        return value.lower()


class PasswordResetConfirmSerializer(serializers.Serializer):
    """
    Maneja el cambio final de la contraseña.
    Valida el Token criptográfico y el ID del usuario codificado.
    """
    # write_only=True asegura que la password nunca se devuelva en la respuesta API
    password = serializers.CharField(write_only=True, min_length=8)
    token = serializers.CharField()
    uidb64 = serializers.CharField()

    def validate(self, attrs):
        """
        Validación cruzada de Token + Usuario.
        """
        try:
            # 1. Decodificar el ID del usuario desde Base64
            # Esto viene de la URL: /reset-password/<uidb64>/<token>
            uid = urlsafe_base64_decode(attrs['uidb64']).decode()
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            # Si el ID está corrupto o el usuario no existe
            raise serializers.ValidationError("Enlace inválido o usuario no encontrado.")

        # 2. Verificar criptográficamente el Token
        # Django verifica: que sea para este usuario y que no haya expirado (default 3 días).
        if not default_token_generator.check_token(user, attrs['token']):
            raise serializers.ValidationError("El enlace ha expirado o es inválido.")

        # Inyectamos el objeto usuario validado en los datos para que la Vista lo use
        attrs['user'] = user
        return attrs
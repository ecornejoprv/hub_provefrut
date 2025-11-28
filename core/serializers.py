# core/serializers.py

from rest_framework import serializers
from .models import Empresa, Pertenencia

class EmpresaSerializer(serializers.ModelSerializer):
    """
    Traduce el modelo Empresa a JSON simple.
    Usado para mostrar la lista de empresas disponibles al usuario.
    """
    class Meta:
        model = Empresa
        fields = ['id', 'nombre', 'codigo']

class UserContextSerializer(serializers.ModelSerializer):
    """
    Serializador para devolver los datos del usuario actual
    y sus roles.
    """
    empresa_nombre = serializers.CharField(source='empresa.nombre')
    grupo_nombre = serializers.CharField(source='grupo.name')

    class Meta:
        model = Pertenencia
        fields = ['empresa_nombre', 'grupo_nombre']
"""
Serializers VOPT — validação e serialização de dados de entrada/saída.
"""
import re

from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

from .models import Usuario


class CadastroSerializer(serializers.ModelSerializer):
    """Cadastro de novo usuário — PF ou PJ."""

    senha = serializers.CharField(
        write_only=True,   # nunca retorna a senha
        min_length=8,
        max_length=128,
        style={"input_type": "password"},
    )

    class Meta:
        model  = Usuario
        fields = ["nome", "email", "documento", "senha"]

    def validate_senha(self, value):
        erros = []
        if not re.search(r"[A-Z]", value):
            erros.append("uma letra maiúscula")
        if not re.search(r"[0-9]", value):
            erros.append("um número")
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', value):
            erros.append('um caractere especial (!@#$...)')
        if erros:
            raise serializers.ValidationError(
                f"A senha precisa ter: {', '.join(erros)}."
            )
        # Validadores do Django (comprimento, senha comum, etc.)
        validate_password(value)
        return value

    def create(self, validated_data):
        return Usuario.objects.create_user(
            email     = validated_data["email"],
            nome      = validated_data["nome"],
            documento = validated_data["documento"],
            password  = validated_data["senha"],
        )


class UsuarioPublicoSerializer(serializers.ModelSerializer):
    """Dados públicos do usuário — senha nunca exposta."""

    trial_dias_restantes = serializers.IntegerField(read_only=True)

    class Meta:
        model  = Usuario
        fields = [
            "nome", "email", "tipo",
            "trial_ativo", "trial_fim",
            "trial_dias_restantes", "criado_em",
        ]
        read_only_fields = fields

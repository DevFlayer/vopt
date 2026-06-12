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
        write_only=True,
        min_length=8,
        max_length=128,
        style={"input_type": "password"},
    )

    class Meta:
        model  = Usuario
        fields = ["nome", "email", "documento", "senha"]

    def validate_documento(self, value):
        import re
        cpf = re.compile(r"^\d{3}\.\d{3}\.\d{3}-\d{2}$")
        if not cpf.match(value):
            raise serializers.ValidationError(
                "CPF inválido. Use o formato 000.000.000-00."
            )
        return value

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
        validate_password(value)
        return value

    def create(self, validated_data):
        senha = validated_data.pop("senha")
        return Usuario.objects.create_user(
            email     = validated_data["email"],
            nome      = validated_data["nome"],
            documento = validated_data["documento"],
            password  = senha,
        )

class UsuarioPerfilSerializer(serializers.ModelSerializer):
    senha_atual = serializers.CharField(write_only=True, required=False, allow_blank=False, style={"input_type": "password"})
    nova_senha = serializers.CharField(write_only=True, required=False, min_length=8, style={"input_type": "password"})

    class Meta:
        model = Usuario
        fields = [
            "nome",
            "nome_exibicao",
            "email_recuperacao",
            "genero",
            "senha_atual",
            "nova_senha",
        ]
        extra_kwargs = {
            "email_recuperacao": {"required": False, "allow_blank": True},
            "genero": {"required": False, "allow_blank": True},
            "nome_exibicao": {"required": False, "allow_blank": True},
        }

    def validate(self, attrs):
        if attrs.get("nova_senha") and not attrs.get("senha_atual"):
            raise serializers.ValidationError({
                "senha_atual": "Informe a senha atual para alterar a senha."
            })
        return attrs

    def update(self, instance, validated_data):
        nova_senha = validated_data.pop("nova_senha", None)
        senha_atual = validated_data.pop("senha_atual", None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        if nova_senha:
            if not instance.check_password(senha_atual or ""):
                raise serializers.ValidationError({"senha_atual": "Senha atual incorreta."})
            validate_password(nova_senha)
            instance.set_password(nova_senha)

        instance.full_clean()
        instance.save()
        return instance


class UsuarioPublicoSerializer(serializers.ModelSerializer):
    """Dados públicos do usuário — senha nunca exposta."""

    trial_dias_restantes = serializers.IntegerField(read_only=True)

    class Meta:
        model  = Usuario
        fields = [
            "nome", "nome_exibicao", "email", "email_recuperacao", "genero", "tipo",
            "trial_ativo", "trial_fim",
            "trial_dias_restantes", "criado_em",
        ]
        read_only_fields = fields

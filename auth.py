"""
Views de autenticação VOPT.
"""
import logging

from django.contrib.auth import authenticate
from django_ratelimit.decorators import ratelimit
from django.utils.decorators import method_decorator
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from ..serializers import CadastroSerializer
from ..models import Usuario

logger = logging.getLogger("vopt")


class CadastroView(APIView):
    """
    POST /api/auth/cadastro/
    Cria conta para pessoa física (CPF) ou jurídica (CNPJ).
    Rate limit: 5 cadastros/minuto por IP.
    """
    permission_classes = [AllowAny]

    @method_decorator(ratelimit(key="ip", rate="5/m", method="POST", block=True))
    def post(self, request):
        serializer = CadastroSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                {"erro": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Verifica duplicidade com mensagem genérica (não revela se e-mail existe)
        email = serializer.validated_data["email"]
        if Usuario.objects.filter(email=email).exists():
            return Response(
                {"erro": "Não foi possível concluir o cadastro. Verifique os dados."},
                status=status.HTTP_409_CONFLICT,
            )

        usuario = serializer.save()
        logger.info("Novo usuário: %s (%s)", usuario.email, usuario.tipo.upper())

        return Response(
            {
                "mensagem": "Conta criada! Seu período de 30 dias grátis começou.",
                "tipo":       usuario.tipo,
                "trial_dias": usuario.trial_dias_restantes,
            },
            status=status.HTTP_201_CREATED,
        )


class LoginView(APIView):
    """
    POST /api/auth/login/
    Autentica e retorna par de tokens JWT (access + refresh).
    Rate limit: 10 tentativas/minuto por IP — proteção contra força bruta.
    """
    permission_classes = [AllowAny]

    ERRO_GENERICO = Response(
        {"erro": "E-mail ou senha incorretos."},
        status=status.HTTP_401_UNAUTHORIZED,
    )

    @method_decorator(ratelimit(key="ip", rate="10/m", method="POST", block=True))
    def post(self, request):
        email = request.data.get("email", "").strip().lower()
        senha = request.data.get("senha", "")

        if not email or not senha:
            return Response(
                {"erro": "E-mail e senha são obrigatórios."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # authenticate() usa bcrypt internamente — nunca compara texto puro
        usuario = authenticate(request, username=email, password=senha)

        if usuario is None:
            # Mensagem genérica — não revela se o e-mail existe
            logger.warning("Login falhou para: %s", email)
            return LoginView.ERRO_GENERICO

        if not usuario.is_active:
            return Response(
                {"erro": "Conta suspensa. Entre em contato com o suporte."},
                status=status.HTTP_403_FORBIDDEN,
            )

        refresh = RefreshToken.for_user(usuario)
        logger.info("Login OK: %s", usuario.email)

        return Response({
            "access":       str(refresh.access_token),
            "refresh":      str(refresh),
            "tipo":         usuario.tipo,
            "trial_ativo":  usuario.trial_ativo,
            "trial_dias":   usuario.trial_dias_restantes,
        })


class RefreshView(APIView):
    """
    POST /api/auth/refresh/
    Renova o access token usando o refresh token.
    """
    permission_classes = [AllowAny]

    def post(self, request):
        token_str = request.data.get("refresh")
        if not token_str:
            return Response(
                {"erro": "refresh token é obrigatório."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            refresh = RefreshToken(token_str)
            return Response({"access": str(refresh.access_token)})
        except Exception:
            return Response(
                {"erro": "Token inválido ou expirado."},
                status=status.HTTP_401_UNAUTHORIZED,
            )
        
        def cadastrar_usuario(self, request):
        
            serializer = CadastroSerializer(data=request.data)
            if not serializer.is_valid():
                return Response(
                    {"erro": serializer.errors},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            email = serializer.validated_data["email"]
            if Usuario.objects.filter(email=email).exists():
                return Response(
                    {"erro": "Não foi possível concluir o cadastro. Verifique os dados."},
                    status=status.HTTP_409_CONFLICT,
                )

            usuario = serializer.save()
            logger.info("Novo usuário: %s (%s)", usuario.email, usuario.tipo.upper())

            return Response(
                {
                    "mensagem": "Conta criada! Seu período de 30 dias grátis começou.",
                    "tipo":       usuario.tipo,
                    "trial_dias": usuario.trial_dias_restantes,
                },
                status=status.HTTP_201_CREATED,
            )   

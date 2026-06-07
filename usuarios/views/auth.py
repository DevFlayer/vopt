"""
Views de autenticação VOPT.
"""
import logging
import secrets

from django.conf import settings
from django.core.cache import cache
from django.db.models import Q
from django.contrib.auth import authenticate
from django_ratelimit.decorators import ratelimit
from django.utils.decorators import method_decorator
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from ..serializers import CadastroSerializer
from ..models import Usuario
from ..utils_emails import enviar_email_recuperacao

logger = logging.getLogger("vopt")

@api_view(['POST'])
@permission_classes([AllowAny])
@ratelimit(key="ip", rate="5/m", method="POST", block=True)
def cadastrar_usuario(request):
    """
    Endpoint para processar o clique no botão 'Criar conta'.
    """
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

class LoginView(APIView):
    """
    POST /api/auth/login/
    Autentica e retorna par de tokens JWT (access + refresh).
    Rate limit: 10 tentativas/minuto por IP — proteção contra força bruta.
    """
    permission_classes = [AllowAny]

    ERRO_GENERICO = Response(
        {"erro": "E-mail/CPF ou senha incorretos."},
        status=status.HTTP_401_UNAUTHORIZED,
    )

    @method_decorator(ratelimit(key="ip", rate="10/m", method="POST", block=True))
    def post(self, request):
        login_input = request.data.get("email", "").strip()
        senha = request.data.get("senha", "")

        if not login_input or not senha:
            return Response(
                {"erro": "E-mail/CPF e senha são obrigatórios."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Tenta formatar o input caso sejam apenas números (CPF/CNPJ)
        digits = "".join(filter(str.isdigit, login_input))
        formatted_doc = ""
        if len(digits) == 11:
            formatted_doc = f"{digits[:3]}.{digits[3:6]}.{digits[6:9]}-{digits[9:]}"
        elif len(digits) == 14:
            formatted_doc = f"{digits[:2]}.{digits[2:5]}.{digits[5:8]}/{digits[8:12]}-{digits[12:]}"

        # Busca o usuário pelo e-mail, documento exato ou documento formatado
        user_found = Usuario.objects.filter(
            Q(email__iexact=login_input) | Q(documento=login_input) | Q(documento=formatted_doc)
        ).first()

        # Se encontrarmos o usuário, usamos o e-mail dele para a autenticação padrão do Django
        username_to_auth = user_found.email if user_found else login_input
        usuario = authenticate(request, username=username_to_auth, password=senha)

        if usuario is None:
            logger.warning("Login falhou para: %s", login_input)
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

class RecuperarSenhaView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get("email", "").strip().lower()

        if not email:
            return Response(
                {"erro": "E-mail é obrigatório."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Sempre retorna 200 para não revelar se o e-mail existe
        usuario = Usuario.objects.filter(email=email).first()
        if usuario:
            token = secrets.token_urlsafe(32)
            cache.set(f"reset:{token}", email, timeout=1800)  # 30 min
            link = f"{settings.SITE_URL}/redefinir-senha/?token={token}"
            enviar_email_recuperacao(email, link)

        return Response(
            {"mensagem": "Se o e-mail estiver cadastrado, você receberá o link em breve."},
            status=status.HTTP_200_OK,
        )

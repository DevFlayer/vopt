"""Views de perfil do usuário autenticado."""
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from ..serializers import UsuarioPerfilSerializer, UsuarioPublicoSerializer


class PerfilView(APIView):
    """GET /api/usuario/perfil/ — dados do usuário logado (sem senha)."""

    def get(self, request):
        serializer = UsuarioPublicoSerializer(request.user)
        return Response(serializer.data)

    def patch(self, request):
        serializer = UsuarioPerfilSerializer(request.user, data=request.data, partial=True)
        if not serializer.is_valid():
            return Response({"erro": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

        serializer.save()
        return Response(serializer.data)

    def delete(self, request):
        senha = request.data.get("senha_exclusao", "")
        confirma = request.data.get("senha_exclusao_confirma", "")

        if not senha or not confirma:
            return Response(
                {"erro": "Informe a senha duas vezes para confirmar a exclusão."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if senha != confirma:
            return Response(
                {"erro": "As senhas não coincidem."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if not request.user.check_password(senha):
            return Response(
                {"erro": "Senha incorreta."},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        request.user.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class StatusTrialView(APIView):
    """GET /api/usuario/trial/ — dias restantes do período gratuito."""

    def get(self, request):
        u = request.user
        return Response({
            "trial_ativo":    u.trial_ativo,
            "dias_restantes": u.trial_dias_restantes,
            "trial_fim":      u.trial_fim.isoformat(),
        })

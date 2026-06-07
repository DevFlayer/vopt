"""Views de perfil do usuário autenticado."""
from rest_framework.response import Response
from rest_framework.views import APIView

from ..serializers import UsuarioPublicoSerializer


class PerfilView(APIView):
    """GET /api/usuario/perfil/ — dados do usuário logado (sem senha)."""

    def get(self, request):
        serializer = UsuarioPublicoSerializer(request.user)
        return Response(serializer.data)


class StatusTrialView(APIView):
    """GET /api/usuario/trial/ — dias restantes do período gratuito."""

    def get(self, request):
        u = request.user
        return Response({
            "trial_ativo":    u.trial_ativo,
            "dias_restantes": u.trial_dias_restantes,
            "trial_fim":      u.trial_fim.isoformat(),
        })

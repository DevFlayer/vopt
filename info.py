"""Endpoints públicos de informação (sem autenticação)."""
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView


class FuncionalidadesView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        return Response({
            "funcionalidades": [
                "E-mail personalizado (voce@seudominio.com.br)",
                "Interface intuitiva para gestão de e-mails",
                "Armazenamento seguro em nuvem com criptografia",
                "Filtros anti-spam avançados",
                "Acesso para pessoa física sem burocracia",
                "Suporte em português",
            ]
        })


class PlanosView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        return Response({
            "planos": [
                {
                    "nome":      "Trial",
                    "preco":     0.0,
                    "periodo":   "30 dias",
                    "descricao": "Grátis para PF e PJ. Sem cartão de crédito.",
                },
                {
                    "nome":    "Mensal",
                    "preco":   10.0,
                    "moeda":   "BRL",
                    "por":     "usuário/mês",
                },
                {
                    "nome":     "Anual",
                    "preco":    100.0,
                    "moeda":    "BRL",
                    "por":      "usuário/ano",
                    "desconto": "20% OFF",
                },
            ]
        })


class SuporteView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        return Response({
            "canais": [
                {"tipo": "Telefone", "contato": "0800-VOPT"},
                {"tipo": "Chat",     "contato": "Disponível no painel após login"},
                {"tipo": "E-mail",   "contato": "suporte@vopt.com.br"},
            ]
        })


class HealthView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        from django.db import connection
        try:
            connection.ensure_connection()
            db_status = "ok"
        except Exception:
            db_status = "erro"
        return Response({"status": "ok", "db": db_status})

from django.urls import path

from ..views.auth import cadastrar_usuario, LoginView, RefreshView, RecuperarSenhaView

urlpatterns = [
    path("cadastro/", cadastrar_usuario, name="api_cadastro"),
    path("login/", LoginView.as_view(), name="login"),
    path("refresh/", RefreshView.as_view(), name="refresh"),
    path("recuperar-senha/", RecuperarSenhaView.as_view(), name="api_recuperar_senha"),
]

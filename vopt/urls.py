from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView

urlpatterns = [
    path("admin/", admin.site.urls),  # 👈 ADICIONA ISSO

    path("", TemplateView.as_view(template_name="login.html"), name="login"),
    path("cadastro/", TemplateView.as_view(template_name="cadastro.html"), name="pagina_cadastro"),
    path("recuperar-senha/", TemplateView.as_view(template_name="recuperar-senha.html"), name="recuperar-senha"),
    path("mailbox/", TemplateView.as_view(template_name="mailbox.html"), name="mailbox"),
    path("perfil/", TemplateView.as_view(template_name="perfil.html"), name="perfil"),

    path("api/auth/", include("usuarios.urls.auth")),
    path("api/usuario/", include("usuarios.urls.usuario")),
    path("api/info/", include("usuarios.urls.info")),
]
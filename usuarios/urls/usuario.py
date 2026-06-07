from django.urls import path

from ..views.usuario import PerfilView, StatusTrialView

urlpatterns = [
    path("perfil/", PerfilView.as_view(), name="perfil"),
    path("trial/", StatusTrialView.as_view(), name="trial"),
]

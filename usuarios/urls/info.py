from django.urls import path

from ..views.info import FuncionalidadesView, PlanosView, SuporteView, HealthView

urlpatterns = [
    path("funcionalidades/", FuncionalidadesView.as_view(), name="funcionalidades"),
    path("planos/", PlanosView.as_view(), name="planos"),
    path("suporte/", SuporteView.as_view(), name="suporte"),
    path("health/", HealthView.as_view(), name="health"),
]

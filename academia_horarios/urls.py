from django.urls import path
from .views import OfertaView, ComisionDetailView, HorarioCreateView, HorarioUpdateView, HorarioDeleteView, timeslots_api

urlpatterns = [
    path("oferta/", OfertaView.as_view(), name="panel_oferta"),
    path("comisiones/<int:pk>/", ComisionDetailView.as_view(), name="panel_comision"),
    path("horarios/nuevo/", HorarioCreateView.as_view(), name="panel_horario_new"),
    path("horarios/<int:pk>/editar/", HorarioUpdateView.as_view(), name="panel_horario_edit"),
    path("horarios/<int:pk>/borrar/", HorarioDeleteView.as_view(), name="panel_horario_del"),
    path("horarios/api/timeslots/", timeslots_api, name="timeslots_api"),
]
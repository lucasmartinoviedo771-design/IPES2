from django.urls import path
from .views import OfertaView, comision_detail, HorarioDeleteView, timeslots_api

urlpatterns = [
    path("oferta/", OfertaView.as_view(), name="panel_oferta"),
    path("comisiones/<int:pk>/", comision_detail, name="panel_comision"),
    path("horarios/<int:pk>/borrar/", HorarioDeleteView.as_view(), name="panel_horario_del"),
    path("horarios/api/timeslots/", timeslots_api, name="timeslots_api"),
]
from django.urls import path

from .views import (
    HorarioDeleteView,
    OfertaView,
    abrir_paralela,
    cargar_horario,
    comision_detail,
    timeslots_api,
)

app_name = "academia_horarios"

urlpatterns = [
    path("oferta/", OfertaView.as_view(), name="panel_oferta"),
    path("horarios/cargar/", cargar_horario, name="cargar_horario"),
    path(
        "horarios/abrir-paralela/<int:plan_id>/<int:periodo_id>/",
        abrir_paralela,
        name="abrir_paralela",
    ),
    path("comisiones/<int:pk>/", comision_detail, name="panel_comision"),
    path("horarios/<int:pk>/borrar/", HorarioDeleteView.as_view(), name="panel_horario_del"),
    path("horarios/api/timeslots/", timeslots_api, name="timeslots_api"),
]

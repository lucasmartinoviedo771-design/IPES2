from django.urls import path
from .views import (
    DashboardView,
    EstudianteListView, EstudianteDetailView, NuevoEstudianteView,
    DocenteListView, NuevoDocenteView,
    InscribirMateriaView, InscribirFinalView, InscripcionProfesoradoView,
    CartonEstudianteView, HistoricoEstudianteView,
    SwitchRoleView,
    CorrelatividadesView,
)
from . import api
from . import views
from . import views_api

app_name = "ui"

urlpatterns = [
    path("dashboard", DashboardView.as_view(), name="dashboard"),

    # Personas
    path("estudiantes", EstudianteListView.as_view(), name="estudiantes_list"),
    path("estudiantes/<int:pk>", EstudianteDetailView.as_view(), name="estudiantes_detail"),
    path("personas/estudiantes/nuevo", NuevoEstudianteView.as_view(), name="estudiante_nuevo"),
    path("docentes", DocenteListView.as_view(), name="docentes_list"),
    path("personas/docentes/nuevo", NuevoDocenteView.as_view(), name="docente_nuevo"),

    # Inscripciones
    path("inscripciones/carrera", InscripcionProfesoradoView.as_view(), name="inscribir_carrera"),
    path("inscribir/materias", InscribirMateriaView.as_view(), name="inscribir_materias"),
    path("inscripciones/mesa-final", InscribirFinalView.as_view(), name="inscribir_final"),
    path("inscripciones/profesorado", InscripcionProfesoradoView.as_view(), name="inscripcion_profesorado"),

    # Académico
    path("academico/correlatividades", CorrelatividadesView.as_view(), name="correlatividades"),

    # Cartón e Histórico del Estudiante
    path("estudiante/carton", CartonEstudianteView.as_view(), name="carton_estudiante"),
    path("estudiante/historico", HistoricoEstudianteView.as_view(), name="historico_estudiante"),

    # Cambiar rol
    path("cambiar-rol", SwitchRoleView.as_view(), name="switch_role"),

    # API Endpoints
    path("api/planes/", views_api.api_planes, name="api_planes"),
    path("api/materias/", views_api.api_materias, name="api_materias"),
    path("api/docentes/", views_api.api_docentes, name="api_docentes"),
    
    path("api/turnos", views_api.api_turnos, name="api_turnos"),
    path("api/horarios-ocupados/", views_api.api_horarios_ocupados, name="api_horarios_ocupados"),
    path("api/cohortes", api.api_cohortes_por_plan, name="api_cohortes"),
    path("api/correlatividades", api.api_correlatividades_por_espacio, name="api_correlatividades_por_espacio"),
    path("api/calcular-estado-administrativo/", api.api_calcular_estado_administrativo, name="api_calcular_estado_administrativo"),

    # Rutas para comisiones
    path("comisiones/<int:pk>/asignar-docente/", views.asignar_docente, name="asignar_docente"),
    path("comisiones/<int:pk>/agregar-horario/", views.agregar_horario, name="agregar_horario"),

    # Oferta
    path("oferta", views.oferta_por_plan, name="oferta_por_plan"),
]

from django.urls import reverse_lazy
from django.views.generic import CreateView
from django.contrib import messages

from .forms import InscripcionCarreraForm, InscripcionMateriaForm, InscripcionMesaForm

class BaseCreateView(CreateView):
    template_name = "inscripciones/form_base.html"
    success_url = reverse_lazy("ui:dashboard")  # Ajustado a tu proyecto
    page_title = ""
    submit_label = "Guardar"
    nav_blocks = {}  # qué items del menú dejar activos

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["page_title"] = self.page_title
        ctx["submit_label"] = self.submit_label
        ctx.update(self.nav_blocks)
        return ctx

    def form_valid(self, form):
        resp = super().form_valid(form)
        messages.success(self.request, f"{self.page_title} registrada correctamente.")
        return resp

class InscripcionCarreraCreate(BaseCreateView):
    form_class = InscripcionCarreraForm
    page_title = "Inscripción a Carrera"
    submit_label = "Guardar Inscripción"
    nav_blocks = {
        "nav_insc": "active",
        "nav_insc_carrera": "active",
    }

class InscripcionMateriaCreate(BaseCreateView):
    form_class = InscripcionMateriaForm
    page_title = "Inscripción a Materia"
    submit_label = "Guardar Inscripción"
    nav_blocks = {
        "nav_insc": "active",
        "nav_insc_materia": "active",
    }

class InscripcionMesaCreate(BaseCreateView):
    form_class = InscripcionMesaForm
    page_title = "Inscripción a Mesa"
    submit_label = "Guardar Inscripción"
    nav_blocks = {
        "nav_insc": "active",
        "nav_insc_mesa": "active",
    }

# ui/forms.py
from django import forms
from academia_core.models import PlanEstudios, Estudiante, Docente

# --- Filtros de Oferta (esto ya lo tenías) ---
ANIOS_CHOICES = [(1, "1°"), (2, "2°"), (3, "3°"), (4, "4°")]
PERIODO_CHOICES = [("", "--")]  # lo vamos a poblar luego desde BD/Periodos reales

class OfertaFilterForm(forms.Form):
    plan = forms.ModelChoiceField(
        queryset=PlanEstudios.objects.select_related("profesorado"),
        required=True,
        label="Plan",
    )
    anio = forms.ChoiceField(choices=ANIOS_CHOICES, required=True, label="Año")
    periodo = forms.ChoiceField(choices=PERIODO_CHOICES, required=False, label="Período")


# --- Formularios simples para Estudiantes/Docentes (ModelForm básico) ---
class EstudianteNuevoForm(forms.ModelForm):
    class Meta:
        model = Estudiante
        fields = "__all__"

class EstudianteEditarForm(EstudianteNuevoForm):
    pass

class NuevoDocenteForm(forms.ModelForm):
    class Meta:
        model = Docente
        fields = "__all__"

class DocenteEditarForm(NuevoDocenteForm):
    pass


# --- Constantes que importan algunas views ---
CERT_DOCENTE_LABEL = "Certificado de trabajo docente (opcional)"


# --- Placeholders no funcionales (solo para que el import no rompa) ---
class EstudianteMatricularForm(forms.Form):
    """Pendiente de implementar.”""
    pass

class InscripcionProfesoradoForm(forms.Form):
    """Pendiente: CreateView real. Dejo helpers para que no explote."""
    def compute_estado_admin(self):  # las views llaman a esto
        return None
    def _calculate_estado_from_data(self, *args, **kwargs):
        return None

class CorrelatividadesForm(forms.Form):
    """Pendiente de implementar.”""
    pass

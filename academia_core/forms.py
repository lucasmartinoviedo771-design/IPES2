from django import forms
from .models import InscripcionCarrera, InscripcionMateria, InscripcionMesa

class BaseStyledModelForm(forms.ModelForm):
    """Aplica clases del tema automáticamente (input/select/textarea/file)."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for f in self.fields.values():
            w = f.widget.__class__.__name__
            base = "input"
            if "Select" in w: base = "select"
            if "Textarea" in w: base = "textarea"
            if "FileInput" in w: base = "file"
            f.widget.attrs["class"] = (f.widget.attrs.get("class","") + " " + base).strip()

class InscripcionCarreraForm(BaseStyledModelForm):
    class Meta:
        model = InscripcionCarrera
        fields = ["estudiante", "carrera", "cohorte", "turno", "estado"]
        widgets = {
            "cohorte": forms.NumberInput(attrs={"min":2000, "max":2100}),
            "turno": forms.TextInput(attrs={"placeholder":"Mañana / Tarde / Noche"}),
        }

class InscripcionMateriaForm(BaseStyledModelForm):
    class Meta:
        model = InscripcionMateria
        fields = ["estudiante", "materia", "comision", "estado"]
        widgets = {
            "comision": forms.TextInput(attrs={"placeholder":"A, B, C… (opcional)"}),
        }

class InscripcionMesaForm(BaseStyledModelForm):
    class Meta:
        model = InscripcionMesa
        fields = ["estudiante", "mesa", "condicion", "llamada", "estado"]

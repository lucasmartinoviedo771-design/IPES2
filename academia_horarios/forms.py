from django import forms
from django.core.exceptions import ValidationError
from .models import HorarioClase, TimeSlot, Comision

TURNOS = (
    ("", "— (todos) —"),
    ("M", "Mañana"),
    ("T", "Tarde"),
    ("V", "Vespertino"),
    ("S", "Sábado"),
)

class HorarioClaseForm(forms.ModelForm):
    turno = forms.ChoiceField(choices=TURNOS, required=False, label="Turno")
    bloque = forms.ChoiceField(choices=(), required=True, label="Bloque (día / inicio–fin)")

    class Meta:
        model = HorarioClase
        fields = ["comision", "turno", "bloque", "aula", "docentes", "observaciones"]
        widgets = {"docentes": forms.SelectMultiple(attrs={"size": 6})}

    def clean(self):
        cleaned = super().clean()

        # mapear "bloque" -> timeslot_id si usás el combo de bloque único
        timeslot_id = cleaned.get("timeslot") or cleaned.get("timeslot_id")
        if not timeslot_id and cleaned.get("bloque"):
            try:
                timeslot_id = int(cleaned["bloque"])
                cleaned["timeslot_id"] = timeslot_id
            except (TypeError, ValueError):
                pass

        comision = cleaned.get("comision")
        periodo  = comision.periodo if comision else None
        docentes = cleaned.get("docentes")
        if not all([timeslot_id, periodo, docentes]):
            return cleaned

        conflictos = (
            HorarioClase.objects
            .filter(timeslot_id=timeslot_id, comision__periodo=periodo)
            .filter(docentes__in=docentes)
            .exclude(pk=self.instance.pk)
            .select_related("comision__materia_en_plan__materia", "timeslot")
            .prefetch_related("docentes")
            .distinct()
        )

        if conflictos.exists():
            by_doc = {}
            doc_ids = {d.id for d in docentes}
            for hc in conflictos:
                for d in hc.docentes.all():
                    if d.id in doc_ids:
                        by_doc.setdefault(d.apellido_nombre, []).append(hc)

            msgs = []
            for nombre_doc, hcs in by_doc.items():
                refs = []
                for hc in hcs:
                    # nombre de la materia (si existe el encadenado)
                    nombre_mat = getattr(getattr(getattr(hc.comision, "materia_en_plan", None), "materia", None), "nombre", "(materia)")
                    refs.append(
                        f"{nombre_mat} (Año {hc.comision.materia_en_plan.anio}, Período {hc.comision.periodo}, "
                        f"Día {hc.timeslot.dia_semana} {hc.timeslot.inicio:%H:%M}-{hc.timeslot.fin:%H:%M})")
                msgs.append(f"- {nombre_doc} ya está asignado/a en: " + "; ".join(refs))

            raise ValidationError({
                "docentes": "Conflicto de disponibilidad docente en este bloque.\n" + "\n".join(msgs)
            })

        return cleaned
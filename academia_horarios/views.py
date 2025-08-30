from django.views.generic import TemplateView, DetailView, CreateView, UpdateView, DeleteView, ListView
from django.shortcuts import redirect
from django.urls import reverse, reverse_lazy
from django.db.models import Sum
from django.contrib import messages
from .models import Plan, MateriaEnPlan, Comision, Periodo, HorarioClase, hc_asignadas, hc_requeridas, TimeSlot
from .forms import HorarioClaseForm
from datetime import time
from django.http import JsonResponse

class OfertaView(TemplateView):
    template_name = "academia_horarios/oferta_list.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        plan_id = self.request.GET.get("plan")
        anio = self.request.GET.get("anio")
        periodo_id = self.request.GET.get("periodo")
        ctx["planes"] = Plan.objects.all().order_by("profesorados__nombre", "nombre")
        ctx["periodos"] = Periodo.objects.all().order_by("-ciclo_lectivo", "cuatrimestre")
        ctx["anio_sel"] = anio
        ctx["plan_sel"] = int(plan_id) if plan_id else None
        ctx["periodo_sel"] = int(periodo_id) if periodo_id else None
        ctx["rows"] = []
        if plan_id and anio and periodo_id:
            meps = MateriaEnPlan.objects.filter(plan_id=plan_id, anio=anio).select_related("plan", "materia")
            periodo = Periodo.objects.get(pk=periodo_id)
            rows = []
            for mep in meps:
                comi_unica = Comision.objects.filter(materia_en_plan=mep, periodo=periodo, nombre="Única").first()
                asignadas = hc_asignadas(comi_unica) if comi_unica else 0
                requeridas = hc_requeridas(mep, periodo)
                rows.append({
                    "mep": mep,
                    "periodo": periodo,
                    "comision": comi_unica,
                    "asignadas": asignadas,
                    "requeridas": requeridas,
                    "estado": "ok" if asignadas == requeridas else ("faltan" if asignadas < requeridas else "excedido"),
                })
            ctx["rows"] = rows
        return ctx

    def post(self, request, *args, **kwargs):
        action = request.POST.get("action")
        if action == "desdoblar":
            plan_id = request.POST.get("plan")
            anio = request.POST.get("anio")
            periodo_id = request.POST.get("periodo")
            nombre = request.POST.get("nombre", "B").strip() or "B"
            periodo = Periodo.objects.get(pk=periodo_id)
            meps = MateriaEnPlan.objects.filter(plan_id=plan_id, anio=anio)
            created = 0
            for mep in meps:
                obj, was_created = Comision.objects.get_or_create(
                    materia_en_plan=mep, periodo=periodo, nombre=nombre,
                    defaults={"turno": Comision.objects.filter(materia_en_plan=mep, periodo=periodo).first().turno if Comision.objects.filter(materia_en_plan=mep, periodo=periodo).exists() else "manana",}
                )
                if was_created:
                    created += 1
            messages.success(request, f"Comisiones '{nombre}' creadas: {created}")
        return redirect(f"{reverse('panel_oferta')}?plan={request.POST.get('plan')}&anio={request.POST.get('anio')}&periodo={request.POST.get('periodo')}")

class ComisionDetailView(DetailView):
    template_name = "academia_horarios/comision_detail.html"
    model = Comision

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        comi: Comision = self.object
        mep = comi.materia_en_plan
        # req = hc_requeridas(mep, comi.periodo) # Lógica anterior, la reemplazamos
        # asign = hc_asignadas(comi) # Lógica anterior

        # Nueva lógica de topes
        horas_tope = comi.horas_catedra_tope
        horas_asignadas = comi.horas_asignadas_en_periodo()
        horas_restantes = comi.horas_restantes_en_periodo()
        bloqueado_por_tope = (horas_tope is not None and horas_restantes == 0)

        ctx.update({
            "horarios": comi.horarios.select_related("timeslot").prefetch_related("docentes"),
            "form": HorarioClaseForm(initial={"comision": comi.id}),
            "horas_tope": horas_tope,
            "horas_asignadas": horas_asignadas,
            "horas_restantes": horas_restantes,
            "bloqueado_por_tope": bloqueado_por_tope,
        })
        return ctx

class HorarioCreateView(CreateView):
    template_name = "academia_horarios/horario_form.html"
    form_class = HorarioClaseForm

    def get_initial(self):
        ini = super().get_initial()
        if "comision_id" in self.request.GET:
            ini["comision"] = self.request.GET.get("comision_id")
        return ini

    def get_success_url(self):
        comision_id = self.object.comision_id
        return reverse("panel_comision", args=[comision_id])

class HorarioUpdateView(UpdateView):
    template_name = "academia_horarios/horario_form.html"
    form_class = HorarioClaseForm
    model = HorarioClase
    def get_success_url(self):
        return reverse("panel_comision", args=[self.object.comision_id])

class HorarioDeleteView(DeleteView):
    template_name = "academia_horarios/confirm_delete.html"
    model = HorarioClase
    def get_success_url(self):
        return reverse("panel_comision", args=[self.object.comision_id])


from django.views.decorators.http import require_GET


# --- API --- 

TURNOS = {
    "m":   (time(7,45),  time(12,45)),
    "t":     (time(13,0),  time(18,0)),
    "v":(time(18,10), time(23,10)),
    "s":    (time(9,0),   time(14,0)),
}

def _norm_dia(v):
    # acepta "1..6" o nombres: lunes..sabado
    nombres = {"lunes":1,"martes":2,"miercoles":3,"miércoles":3,"jueves":4,"viernes":5,"sabado":6,"sábado":6}
    s = str(v).strip().lower()
    if s in nombres: return nombres[s]
    try:
        i = int(s)
        if 1 <= i <= 6: return i
    except (TypeError, ValueError):
        pass
    return None

def _norm_turno(s):
    s = (s or "").strip().lower()
    # quitar acentos
    s = s.replace("ñ","n").replace("á","a").replace("é","e").replace("í","i").replace("ó","o").replace("ú","u")
    return s

@require_GET
def timeslots_api(request):
    dia = _norm_dia(request.GET.get("dia"))
    turno = _norm_turno(request.GET.get("turno"))
    
    qs = TimeSlot.objects.all()

    if dia:
        qs = qs.filter(dia_semana=dia)
    
    rango = TURNOS.get(turno)
    if rango:
        desde, hasta = rango
        qs = qs.filter(inicio__gte=desde, fin__lte=hasta)

    qs = qs.order_by("dia_semana", "inicio")

    items = [{"id": t.id, "label": f"{t.get_dia_semana_display()} {t.inicio:%H:%M}–{t.fin:%H:%M}"} for t in qs]
    return JsonResponse({"ok": True, "items": items})
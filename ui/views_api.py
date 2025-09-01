import json
import logging

from django.db.models import F, Value
from django.db.models.functions import Concat
from django.http import JsonResponse
from django.utils import timezone
from django.views.decorators.http import require_GET, require_http_methods

# Importaciones de modelos necesarios
from academia_core.models import Docente, EspacioCurricular, PlanEstudios
from academia_horarios.models import Horario

logger = logging.getLogger(__name__)


@require_GET
def api_planes(request):
    carrera_id = request.GET.get("carrera")
    qs = (
        PlanEstudios.objects.filter(profesorado_id=carrera_id, vigente=True)
        .order_by("nombre")
        .values("id", "nombre")
        if carrera_id
        else []
    )
    return JsonResponse({"results": list(qs)}, status=200)


@require_GET
def api_materias(request):
    params = request.GET.dict()
    logger.info("api_materias GET params=%s", params)

    plan_id = params.get("plan") or params.get("plan_id")
    carrera_id = params.get("carrera") or params.get("carrera_id")

    if not plan_id:
        return JsonResponse(
            {"error": "Falta parámetro plan/plan_id", "recibido": params}, status=400
        )

    try:
        qs = EspacioCurricular.objects.filter(plan_id=plan_id)
        if carrera_id:
            qs = qs.filter(plan__profesorado_id=carrera_id)

        qs = qs.order_by("anio", "cuatrimestre", "nombre")
        data = [{"id": m.id, "nombre": m.nombre, "horas": m.horas} for m in qs]
        logger.info("api_materias OK plan=%s carrera=%s count=%s", plan_id, carrera_id, len(data))
        return JsonResponse({"results": data})
    except Exception as e:
        logger.error("api_materias error: %s", e, exc_info=True)
        return JsonResponse({"results": [], "error": str(e)}, status=500)


@require_GET
def api_docentes(request):
    carrera_id = request.GET.get("carrera")
    materia_id = request.GET.get("materia")
    results = []
    if carrera_id and materia_id:
        try:
            qs = (
                Docente.objects.filter(
                    espacios__id=materia_id, espacios__plan__profesorado_id=carrera_id
                )
                .distinct()
                .annotate(nombre=Concat(F("apellido"), Value(", "), F("nombre")))
                .values("id", "nombre")
                .order_by("apellido", "nombre")
            )
            results = list(qs)
        except Exception as e:
            logger.error("api_docentes error: %s", e, exc_info=True)
            return JsonResponse({"results": [], "error": str(e)}, status=500)

    return JsonResponse({"results": results}, status=200)


def api_turnos(request):
    """
    Devuelve los turnos válidos para armar horarios.
    """
    data = {
        "turnos": [
            {"value": "manana", "label": "Mañana"},
            {"value": "tarde", "label": "Tarde"},
            {"value": "vespertino", "label": "Vespertino"},
            {"value": "sabado", "label": "Sábado (Mañana)"},
        ]
    }
    return JsonResponse(data)


@require_GET
def api_horarios_ocupados(request):
    # params: turno, docente?, aula?
    turno_slug = request.GET.get("turno")  # El JS actual manda el slug
    docente_id = request.GET.get("docente") or None
    aula_id = request.GET.get("aula") or None

    ocupados = []
    if turno_slug:
        try:
            # Asumo que el modelo Horario usa el CharField de Turno, no el nuevo TurnoModel
            qs = Horario.objects.filter(turno=turno_slug, activo=True)

            if docente_id:
                ocupados.extend(
                    list(qs.filter(docente_id=docente_id).values("dia", "hora_inicio", "hora_fin"))
                )

            if aula_id:
                ocupados.extend(
                    list(qs.filter(aula_id=aula_id).values("dia", "hora_inicio", "hora_fin"))
                )
        except Exception as e:
            logger.error("api_horarios_ocupados error: %s", e, exc_info=True)
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"ocupados": ocupados})


# ------------------------------
# Helpers
# ------------------------------


def _combo_key(carrera, plan, materia, turno):
    # clave única de la cátedra (puedes sumar comision si luego lo agregas)
    return f"{carrera}:{plan}:{materia}:{turno}"


def _get_drafts_store(request):
    # espacio en sesión: { key -> {"slots": set([(d,h), ...]), "version": int, "updated": iso} }
    return request.session.setdefault("horario_drafts", {})


def _parse_slot_from_request(data):
    # d: 1..6 (lun..sab), hhmm: "07:45"
    try:
        d = int(data.get("day"))
        hhmm = str(data.get("hhmm"))
    except Exception:
        d, hhmm = None, None
    return d, hhmm


# ------------------------------
# GET: grilla guardada para la cátedra
# ------------------------------
@require_http_methods(["GET"])
def api_horario_grid(request):
    carrera = request.GET.get("carrera", "")
    plan = request.GET.get("plan", "")
    materia = request.GET.get("materia", "")
    turno = request.GET.get("turno", "")

    key = _combo_key(carrera, plan, materia, turno)
    drafts = _get_drafts_store(request)
    entry = drafts.get(key, {"slots": [], "version": 0, "updated": None})

    # serializamos como lista de objetos {d: int, hhmm: "07:45"}
    slots = [{"d": d, "hhmm": hh} for (d, hh) in entry.get("slots", [])]

    return JsonResponse(
        {
            "ok": True,
            "key": key,
            "slots": slots,
            "count": len(slots),
            "version": entry.get("version", 0),
            "updated": entry.get("updated"),
        }
    )


# ------------------------------
# POST: toggle de un bloque (autosave)
# ------------------------------
@require_http_methods(["POST"])
def api_horario_toggle(request):
    try:
        data = json.loads(request.body.decode("utf-8"))
    except Exception:
        return JsonResponse({"ok": False, "error": "JSON inválido"}, status=400)

    carrera = data.get("carrera", "")
    plan = data.get("plan", "")
    materia = data.get("materia", "")
    turno = data.get("turno", "")
    selected = bool(data.get("selected", True))
    day, hhmm = _parse_slot_from_request(data)

    if not (carrera and plan and materia and turno and day and hhmm):
        return JsonResponse({"ok": False, "error": "Parámetros incompletos"}, status=400)

    key = _combo_key(carrera, plan, materia, turno)
    drafts = _get_drafts_store(request)

    entry = drafts.setdefault(key, {"slots": set(), "version": 0, "updated": None})
    # como la sesión no es json, guardamos set como lista para persistir
    slots = set(tuple(i) for i in entry.get("slots") or [])
    tup = (day, hhmm)

    if selected:
        slots.add(tup)
    else:
        slots.discard(tup)

    entry["slots"] = list(slots)
    entry["version"] = int(entry.get("version", 0)) + 1
    entry["updated"] = timezone.now().isoformat(timespec="seconds")
    drafts[key] = entry
    request.session.modified = True

    return JsonResponse(
        {
            "ok": True,
            "selected": selected,
            "count": len(slots),
            "version": entry["version"],
            "updated": entry["updated"],
        }
    )

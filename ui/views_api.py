import logging
from django.http import JsonResponse
from django.views.decorators.http import require_GET
from django.db.models import Value, F
from django.db.models.functions import Concat

# Importaciones de modelos necesarios
from academia_core.models import PlanEstudios, EspacioCurricular, Docente
from academia_horarios.models import Horario, Bloque, TurnoModel

logger = logging.getLogger(__name__)

@require_GET
def api_planes(request):
    carrera_id = request.GET.get('carrera')
    qs = PlanEstudios.objects.filter(profesorado_id=carrera_id, vigente=True).order_by('nombre').values('id', 'nombre') if carrera_id else []
    return JsonResponse({'results': list(qs)}, status=200)

@require_GET
def api_materias(request):
    params = request.GET.dict()
    logger.info("api_materias GET params=%s", params)

    plan_id = params.get('plan') or params.get('plan_id')
    carrera_id = params.get('carrera') or params.get('carrera_id')

    if not plan_id:
        return JsonResponse({
            'error': 'Falta parámetro plan/plan_id',
            'recibido': params
        }, status=400)

    try:
        qs = EspacioCurricular.objects.filter(plan_id=plan_id)
        if carrera_id:
            qs = qs.filter(plan__profesorado_id=carrera_id)

        qs = qs.order_by('anio', 'cuatrimestre', 'nombre')
        data = [{'id': m.id, 'nombre': m.nombre, 'horas': m.horas} for m in qs]
        logger.info("api_materias OK plan=%s carrera=%s count=%s", plan_id, carrera_id, len(data))
        return JsonResponse({'results': data})
    except Exception as e:
        logger.error("api_materias error: %s", e, exc_info=True)
        return JsonResponse({'results': [], 'error': str(e)}, status=500)

@require_GET
def api_docentes(request):
    carrera_id = request.GET.get('carrera')
    materia_id = request.GET.get('materia')
    results = []
    if carrera_id and materia_id:
        try:
            qs = (Docente.objects
                  .filter(espacios__id=materia_id, espacios__plan__profesorado_id=carrera_id)
                  .distinct()
                  .annotate(nombre=Concat(F('apellido'), Value(', '), F('nombre')))
                  .values('id', 'nombre')
                  .order_by('apellido', 'nombre'))
            results = list(qs)
        except Exception as e:
            logger.error("api_docentes error: %s", e, exc_info=True)
            return JsonResponse({'results': [], 'error': str(e)}, status=500)
            
    return JsonResponse({'results': results}, status=200)



def api_turnos(request):
    """
    Devuelve los turnos válidos para armar horarios.
    """
    data = {
        "turnos": [
            {"value": "manana",    "label": "Mañana"},
            {"value": "tarde",     "label": "Tarde"},
            {"value": "vespertino","label": "Vespertino"},
            {"value": "sabado",    "label": "Sábado (Mañana)"},
        ]
    }
    return JsonResponse(data)


@require_GET
def api_horarios_ocupados(request):
    # params: turno, docente?, aula?
    turno_slug = request.GET.get('turno') # El JS actual manda el slug
    docente_id = request.GET.get('docente') or None
    aula_id    = request.GET.get('aula') or None

    ocupados = []
    if turno_slug:
        try:
            # Asumo que el modelo Horario usa el CharField de Turno, no el nuevo TurnoModel
            qs = Horario.objects.filter(turno=turno_slug, activo=True)
            
            if docente_id:
                ocupados.extend(list(qs.filter(docente_id=docente_id).values('dia', 'hora_inicio', 'hora_fin')))

            if aula_id:
                ocupados.extend(list(qs.filter(aula_id=aula_id).values('dia', 'hora_inicio', 'hora_fin')))
        except Exception as e:
            logger.error("api_horarios_ocupados error: %s", e, exc_info=True)
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({"ocupados": ocupados})
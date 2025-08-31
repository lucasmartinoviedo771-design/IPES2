from django.http import JsonResponse
from academia_core.models import PlanEstudios as Plan

def api_planes(request):
    prof_id = request.GET.get('profesorado') or request.GET.get('prof') or ''
    planes_qs = Plan.objects.filter(profesorado_id=prof_id).values('id','nombre') if prof_id else []
    return JsonResponse({'planes': list(planes_qs)})
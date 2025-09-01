# academia_core/views.py
import io
import os
from collections import defaultdict
from datetime import date

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http import HttpResponse, HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render
from django.template.loader import get_template
from django.utils.text import slugify
from xhtml2pdf import pisa

from .models import (
    DocenteEspacio,
    EspacioCurricular,
    Estudiante,
    EstudianteProfesorado,
    Movimiento,
    PlanEstudios,
    Profesorado,
)


# ---------- Helpers de formato ----------
def _fmt_fecha(d):
    return d.strftime("%d/%m/%Y") if d else ""


def _fmt_nota(m):
    if m.nota_num is not None:
        return str(m.nota_num).rstrip("0").rstrip(".")
    return m.nota_texto or ""


# Resolver rutas /media y /static cuando generamos PDF
def _link_callback(uri):
    if uri.startswith(settings.MEDIA_URL):
        path = os.path.join(settings.MEDIA_ROOT, uri.replace(settings.MEDIA_URL, ""))
        return path
    if uri.startswith(getattr(settings, "STATIC_URL", "/static/")):
        static_root = getattr(settings, "STATIC_ROOT", "")
        if static_root:
            return os.path.join(static_root, uri.replace(settings.STATIC_URL, ""))
    # Si es una URL absoluta http(s), xhtml2pdf suele bloquear; devolvemos tal cual.
    return uri


# ---------- Permisos ----------
def _puede_ver_carton(user, prof, dni):
    if not user.is_authenticated:
        return False
    # superuser / staff
    if getattr(user, "is_superuser", False) or getattr(user, "is_staff", False):
        return True

    perfil = getattr(user, "perfil", None)
    if not perfil:
        return False

    if perfil.rol == "SECRETARIA":
        return True

    if perfil.rol == "ESTUDIANTE":
        return bool(perfil.estudiante) and perfil.estudiante.dni == dni

    if perfil.rol in ("BEDEL", "TUTOR"):
        return prof in perfil.profesorados_permitidos.all()

    if perfil.rol == "DOCENTE" and perfil.docente:
        # puede ver cartones del profesorado donde dicta algún espacio
        return perfil.docente.espacios.filter(profesorado=prof).exists()

    return False


# ---------- Helpers para slugs (sin necesitar campos en DB) ----------
def _get_prof_by_slug(prof_slug: str) -> Profesorado:
    for p in Profesorado.objects.all():
        if slugify(p.nombre) == prof_slug:
            return p
    raise Profesorado.DoesNotExist


def _get_plan_by_res_slug(prof: Profesorado, res_slug: str) -> PlanEstudios:
    # "1935-14" -> "1935/14"
    resol = (res_slug or "").replace("-", "/")
    return PlanEstudios.objects.get(profesorado=prof, resolucion=resol)


def _ensure_slug_attrs(prof: Profesorado, plan: PlanEstudios):
    # Les agregamos atributos .slug y .resolucion_slug en runtime para los templates
    try:
        prof.slug = getattr(prof, "slug", slugify(prof.nombre))
    except Exception:
        prof.slug = slugify(prof.nombre)
    try:
        plan.resolucion_slug = getattr(
            plan, "resolucion_slug", (plan.resolucion or "").replace("/", "-")
        )
    except Exception:
        plan.resolucion_slug = (plan.resolucion or "").replace("/", "-")


# ---------- Builder base (reutilizable) ----------
def _build_carton_ctx_base(prof, plan, dni: str):
    """
    Construye el contexto del cartón para un profesorado y plan dados.
    Lo usan la vista fija de Primaria y la vista genérica por slugs.
    """
    # Estudiante e inscripción
    estudiante = get_object_or_404(Estudiante, dni=dni)
    insc = get_object_or_404(EstudianteProfesorado, estudiante=estudiante, profesorado=prof)

    # Espacios del plan
    espacios = EspacioCurricular.objects.filter(profesorado=prof, plan=plan).order_by(
        "anio", "cuatrimestre", "nombre"
    )

    # Todos los movimientos del alumno en esos espacios (relación inversa)
    movs_qs = insc.movimientos.filter(espacio__in=espacios).select_related("espacio")

    # Agrupar por espacio
    por_espacio = defaultdict(list)
    for m in movs_qs:
        por_espacio[m.espacio_id].append(m)

    bloques = []
    for e in espacios:
        movs = por_espacio.get(e.id, [])

        # Orden cronológico asc; si empatan fecha: REG antes que FIN; luego id asc.
        movs.sort(key=lambda m: (m.fecha or date.min, 0 if m.tipo == "REG" else 1, m.id))

        filas = []
        for m in movs:
            row = {
                "reg_fecha": "",
                "reg_cond": "",
                "reg_nota": "",
                "fin_fecha": "",
                "fin_cond": "",
                "fin_nota": "",
                "folio": "",
                "libro": "",
            }
            if m.tipo == "REG":
                row["reg_fecha"] = _fmt_fecha(m.fecha)
                row["reg_cond"] = m.condicion
                row["reg_nota"] = _fmt_nota(m)
            else:  # FIN
                row["fin_fecha"] = _fmt_fecha(m.fecha)
                row["fin_cond"] = m.condicion
                row["fin_nota"] = _fmt_nota(m)
                row["folio"] = m.folio
                row["libro"] = m.libro
            filas.append(row)

        if not filas:
            filas = [
                {
                    "reg_fecha": "",
                    "reg_cond": "",
                    "reg_nota": "",
                    "fin_fecha": "",
                    "fin_cond": "",
                    "fin_nota": "",
                    "folio": "",
                    "libro": "",
                }
            ]

        bloques.append(
            {
                "anio": e.anio,
                "cuatri": e.cuatrimestre,
                "espacio": e.nombre,
                "rows": filas,
            }
        )

    # Slugs calculados (para templates que los usen)
    _ensure_slug_attrs(prof, plan)

    return {
        "profesorado": prof,
        "plan": plan,
        "estudiante": estudiante,
        "inscripcion": insc,
        "bloques": bloques,
    }


# ---------- Builder original: Primaria fija ----------
def _build_carton_ctx(dni: str):
    prof = get_object_or_404(Profesorado, nombre="Profesorado de Educación Primaria")
    plan = get_object_or_404(PlanEstudios, profesorado=prof, resolucion="1935/14")
    return _build_carton_ctx_base(prof, plan, dni)


# ---------- Vistas HTML / PDF (Primaria) ----------
@login_required
def carton_primaria_por_dni(request, dni):
    ctx = _build_carton_ctx(dni)
    if not _puede_ver_carton(request.user, ctx["profesorado"], dni):
        return HttpResponseForbidden("No tenés permiso para ver este cartón.")
    return render(request, "carton_primaria.html", ctx)


@login_required
def carton_primaria_pdf(request, dni):
    ctx = _build_carton_ctx(dni)
    if not _puede_ver_carton(request.user, ctx["profesorado"], dni):
        return HttpResponseForbidden("No tenés permiso para ver este cartón.")
    html = get_template("carton_primaria.html").render(ctx)
    out = io.BytesIO()
    pisa.CreatePDF(html, dest=out, encoding="utf-8", link_callback=_link_callback)
    resp = HttpResponse(out.getvalue(), content_type="application/pdf")
    resp["Content-Disposition"] = f'inline; filename="carton_{dni}.pdf"'
    return resp


# ---------- Vista GENÉRICA por slugs (HTML) ----------
@login_required
def carton_por_prof_y_plan(request, prof_slug, res_slug, dni):
    """
    Ejemplo URL:
    /carton/profesorado-de-educacion-primaria/1935-14/40000002/
    """
    try:
        prof = _get_prof_by_slug(prof_slug)
        plan = _get_plan_by_res_slug(prof, res_slug)
    except Exception:
        return HttpResponseForbidden("Plan o profesorado inválido.")
    if not _puede_ver_carton(request.user, prof, dni):
        return HttpResponseForbidden("No tenés permiso para ver este cartón.")
    ctx = _build_carton_ctx_base(prof, plan, dni)
    return render(request, "carton_primaria.html", ctx)


# ---------- PDF GENÉRICO por slugs ----------
@login_required
def carton_generico_pdf(request, prof_slug, res_slug, dni):
    try:
        prof = _get_prof_by_slug(prof_slug)
        plan = _get_plan_by_res_slug(prof, res_slug)
    except Exception:
        return HttpResponseForbidden("Plan o profesorado inválido.")
    if not _puede_ver_carton(request.user, prof, dni):
        return HttpResponseForbidden("No tenés permiso para ver este cartón.")
    ctx = _build_carton_ctx_base(prof, plan, dni)
    html = get_template("carton_primaria.html").render(ctx)
    out = io.BytesIO()
    pisa.CreatePDF(html, dest=out, encoding="utf-8", link_callback=_link_callback)
    resp = HttpResponse(out.getvalue(), content_type="application/pdf")
    resp["Content-Disposition"] = f'inline; filename="carton_{dni}.pdf"'
    return resp


# ---------- Buscador por DNI (opcional) ----------
def buscar_carton_primaria(request):
    dni = request.GET.get("dni")
    if dni:
        return redirect("carton_primaria", dni=dni)
    return render(request, "buscar_carton.html")


# ---------- Helpers de estado (Mi Cursada y Docente) ----------
def _es_aprobada(m):
    # Final aprobado por regularidad o libre (>=6) o equivalencia
    if m.tipo == "FIN":
        if m.condicion == "Equivalencia":
            return True
        if m.condicion in ("Regular", "Libre") and m.nota_num is not None and m.nota_num >= 6:
            return True
    # Aprobado/Promoción por REG con nota >=6 (numérica o en texto)
    if m.tipo == "REG" and m.condicion in ("Promoción", "Aprobado"):
        if m.nota_num is not None and m.nota_num >= 6:
            return True
        n = EstudianteProfesorado._parse_num(m.nota_texto)
        if n is not None and n >= 6:
            return True
    return False


def _es_desaprobada(m):
    if m.tipo == "REG" and str(m.condicion).startswith("Desaprobado"):
        return True
    if m.nota_num is not None and m.nota_num < 6:
        return True
    return False


# ---------- Router post-login (evita mandar Bedel/Tutor a /alumno/) ----------
@login_required
def home_router(request):
    perfil = getattr(request.user, "perfil", None)
    # Estudiante → Mi Cursada
    if perfil and perfil.rol == "ESTUDIANTE" and perfil.estudiante:
        return redirect("alumno_home")
    # Staff/otros roles → Admin
    if request.user.is_staff:
        return redirect("/admin/")
    # Fallback: login público
    return redirect("login")




import pytest
from django.apps import apps
from django.core.exceptions import ValidationError

pytestmark = pytest.mark.django_db  # usamos SQLite en CI (USE_SQLITE_FOR_TESTS=1)

def _get_model(app_label, model_name):
    try:
        return apps.get_model(app_label, model_name)
    except LookupError:
        return None

# ==== Ajustá estos nombres si difieren en tu proyecto ====
APP = "academia_horarios"
M_HORARIO = "Horario"
M_DOCENTE = "Docente"
M_COMISION = "Comision"

# Campos típicos; cambialos si tus modelos usan otros nombres
# ej: DIA_FIELD = "dia_semana" o TURNO_FIELD = "turno_codigo"
DIA_FIELD = "dia"
TURNO_FIELD = "turno"
BLOQUE_FIELD = "bloque"

def _must_have_models():
    Horario = _get_model(APP, M_HORARIO)
    Docente = _get_model(APP, M_DOCENTE)
    Comision = _get_model(APP, M_COMISION)
    if not all([Horario, Docente, Comision]):
        faltan = [name for name, m in [(M_HORARIO, Horario),(M_DOCENTE, Docente),(M_COMISION, Comision)] if m is None]
        pytest.skip(f"Faltan modelos: {faltan} — ajustá APP/M_* al inicio del test.")
    return Horario, Docente, Comision

def _mk_docente(Docente, **kw):
    # Ajustá los campos mínimos requeridos por tu modelo Docente
    defaults = dict(nombre="Doc Test", dni="99999999")
    defaults.update(kw)
    return Docente.objects.create(**defaults)

def _mk_comision(Comision, **kw):
    # Ajustá los campos mínimos requeridos por tu modelo Comision
    defaults = dict(nombre="COM-TEST")
    defaults.update(kw)
    return Comision.objects.create(**defaults)

def _mk_horario(Horario, **kw):
    # Ajustá los campos mínimos según tu modelo Horario
    # EJEMPLO típico: docente, comision, dia(int), turno(str o int), bloque(str/int), horas(int)
    defaults = {}
    defaults.update(kw)
    h = Horario(**defaults)
    # Si tu validación está en clean(), lo llamamos antes de guardar
    try:
        h.full_clean()
    except Exception:
        # No falles en el esqueleto; el test “real” lo hará más abajo
        pass
    h.save()
    return h

def test_conflicto_docente_mismo_bloque():
    """No debe permitirse que el mismo docente tenga dos horarios en el mismo día/turno/bloque."""
    Horario, Docente, Comision = _must_have_models()

    # CREA datos mínimos — AJUSTAR nombres de campos
    d = _mk_docente(Docente)
    c = _mk_comision(Comision)

    kwargs = {
        "docente": d,
        "comision": c,
        DIA_FIELD: 1,           # Lunes (ajustá si usás enum distinto)
        TURNO_FIELD: "M",       # Mañana (o el código que uses)
        BLOQUE_FIELD: "1",      # Bloque/Franja
    }
    _mk_horario(Horario, **kwargs)

    with pytest.raises(ValidationError):
        # Segundo horario en el MISMO bloque/día/turno para el mismo docente => debería fallar
        h2 = Horario(**kwargs)
        h2.full_clean()  # si validás en clean()
        h2.save()        # o si validás en save()

def test_tope_de_horas_superado():
    """No debe permitirse superar el tope de horas cátedra por materia/comisión/docente."""
    Horario, Docente, Comision = _must_have_models()

    d = _mk_docente(Docente)
    c = _mk_comision(Comision)

    base = {
        "docente": d,
        "comision": c,
        DIA_FIELD: 2,       # Martes
        TURNO_FIELD: "M",
        BLOQUE_FIELD: "1",
    }

    # Crea horarios hasta llegar al tope — AJUSTÁ el rango según tu política
    # (Si tu tope es p.ej. 4 bloques, creamos 4 OK y el 5º debería fallar)
    top

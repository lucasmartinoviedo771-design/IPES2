import os
import pytest
from django.apps import apps
from django.core.exceptions import ValidationError
from django.db import IntegrityError

# Ejecutar SOLO si RUN_STRICT_HORARIOS_TESTS=1
RUN_STRICT = os.getenv("RUN_STRICT_HORARIOS_TESTS") == "1"
pytestmark = [
    pytest.mark.django_db,
    pytest.mark.skipif(not RUN_STRICT, reason="RUN_STRICT_HORARIOS_TESTS!=1; skipping module"),
]

pytestmark = pytest.mark.django_db

APP = "academia_horarios"
M_HORARIO = "Horario"
M_DOCENTE = "Docente"
M_COMISION = "Comision"

# ← Si tus nombres reales son distintos, cambiá estas 3 constantes
DIA_FIELD = "dia"
TURNO_FIELD = "turno"
BLOQUE_FIELD = "bloque"

# Tope tentativo; si tenés otro real, ajustá aquí o pasalo por env TOPE_HORAS_TEST
TOPE = int(os.getenv("TOPE_HORAS_TEST", "4"))

def _gm(app_label, model_name):
    try:
        return apps.get_model(app_label, model_name)
    except LookupError:
        return None

H = _gm(APP, M_HORARIO)
D = _gm(APP, M_DOCENTE)
C = _gm(APP, M_COMISION)

if not all([H, D, C]):
    pytest.skip("Modelos no encontrados; ajustar APP/M_* antes de activar.")

def _mk_docente(**kw):
    defaults = dict(nombre="Doc Test", dni="99999999")
    defaults.update(kw)
    return D.objects.create(**defaults)

def _mk_comision(**kw):
    defaults = dict(nombre="COM-TEST")
    defaults.update(kw)
    return C.objects.create(**defaults)

def _create_horario(**kw):
    return H.objects.create(**kw)

def test_conflicto_docente_mismo_bloque():
    d = _mk_docente()
    c = _mk_comision()
    base = {"docente": d, "comision": c, DIA_FIELD: 1, TURNO_FIELD: "M", BLOQUE_FIELD: "1"}
    _create_horario(**base)
    with pytest.raises((ValidationError, IntegrityError)):
        h = H(**base)
        h.full_clean()  # por si la validación está en clean()
        h.save()        # o si la validación/constraint es a nivel DB

def test_tope_de_horas_superado():
    d = _mk_docente()
    c = _mk_comision()
    base = {"docente": d, "comision": c, DIA_FIELD: 2, TURNO_FIELD: "M"}
    for i in range(TOPE):
        _create_horario(**{**base, BLOQUE_FIELD: str(i + 1)})
    with pytest.raises((ValidationError, IntegrityError)):
        h = H(**{**base, BLOQUE_FIELD: str(TOPE + 1)})
        h.full_clean()
        h.save()

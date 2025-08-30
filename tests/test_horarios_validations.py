import os
import pytest

if os.getenv("RUN_STRICT_HORARIOS_TESTS") != "1":
    pytest.skip(
        "Saltando tests de validación de horarios. "
        "Activa con RUN_STRICT_HORARIOS_TESTS=1 cuando estén mapeados los campos.",
        allow_module_level=True,
    )

from django.apps import apps
from django.core.exceptions import ValidationError

pytestmark = pytest.mark.django_db

APP = "academia_horarios"
M_HORARIO = "Horario"
M_DOCENTE = "Docente"
M_COMISION = "Comision"

# Ajustá estos nombres cuando lo activemos
DIA_FIELD = "dia"
TURNO_FIELD = "turno"
BLOQUE_FIELD = "bloque"

def _get_model(app_label, model_name):
    try:
        return apps.get_model(app_label, model_name)
    except LookupError:
        return None

def _must_have_models():
    Horario = _get_model(APP, M_HORARIO)
    Docente = _get_model(APP, M_DOCENTE)
    Comision = _get_model(APP, M_COMISION)
    if not all([Horario, Docente, Comision]):
        pytest.skip("Modelos no encontrados; ajustar nombres antes de activar.")
    return Horario, Docente, Comision

def test_conflicto_docente_mismo_bloque():
    Horario, Docente, Comision = _must_have_models()
    d = Docente.objects.create(nombre="Test", dni="99999999")
    c = Comision.objects.create(nombre="COM-TEST")

    kwargs = { "docente": d, "comision": c, DIA_FIELD: 1, TURNO_FIELD: "M", BLOQUE_FIELD: "1" }
    Horario.objects.create(**kwargs)

    with pytest.raises(ValidationError):
        h2 = Horario(**kwargs)
        h2.full_clean()
        h2.save()

def test_tope_de_horas_superado():
    Horario, Docente, Comision = _must_have_models()
    d = Docente.objects.create(nombre="Test", dni="99999999")
    c = Comision.objects.create(nombre="COM-TEST")

    base = { "docente": d, "comision": c, DIA_FIELD: 2, TURNO_FIELD: "M" }
    for i in range(4):  # AJUSTAR al tope real
        Horario.objects.create(**{**base, BLOQUE_FIELD: str(i + 1)})

    with pytest.raises(ValidationError):
        h = Horario(**{**base, BLOQUE_FIELD: "5"})
        h.full_clean()
        h.save()

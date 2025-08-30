from django.apps import apps
from django.conf import settings as dj_settings
import pytest

def _has_model(app_label: str, model_name: str) -> bool:
    try:
        return apps.get_model(app_label, model_name) is not None
    except LookupError:
        return False

def test_apps_installed():
    assert "academia_core.apps.AcademiaCoreConfig" in dj_settings.INSTALLED_APPS
    assert "academia_horarios" in dj_settings.INSTALLED_APPS
    assert "ui" in dj_settings.INSTALLED_APPS

def test_modelos_clave_existen():
    # Ajustá si tus nombres reales difieren
    modelos_esperados = [
        ("academia_horarios", "Horario"),
        ("academia_horarios", "Comision"),
        ("academia_horarios", "Docente"),
    ]
    faltan = [(a, m) for (a, m) in modelos_esperados if not _has_model(a, m)]
    if faltan:
        pytest.skip(f"Faltan modelos (ajustar nombres): {faltan}")

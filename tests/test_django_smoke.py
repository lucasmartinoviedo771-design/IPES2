def test_django_settings(django_settings):
    # El settings se cargó y apunta al módulo correcto
    assert django_settings.ROOT_URLCONF == "academia_project.urls"
    # Comprobamos que apps propias estén instaladas
    assert "academia_horarios" in django_settings.INSTALLED_APPS
    assert "academia_core.apps.AcademiaCoreConfig" in django_settings.INSTALLED_APPS

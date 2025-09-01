from django.apps import AppConfig


class AcademiaCoreConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "academia_core"

    def ready(self):
        # Importa las signals cuando la app se carga
        # Importa los archivos admin.py para registrar los modelos
        import academia_core.admin_config  # noqa: F401

        from . import signals  # noqa: F401

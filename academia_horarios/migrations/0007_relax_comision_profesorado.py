# academia_horarios/migrations/0007_relax_comision_profesorado.py
from django.db import migrations

def relax_profesorado(apps, schema_editor):
    # 👇 Evitar ejecutar en CI (SQLite) u otros motores
    if schema_editor.connection.vendor != "mysql":
        return

    # ⬇️ deja tal cual tu SQL actual (lo que hoy está dentro de c.execute(...))
    with schema_editor.connection.cursor() as c:
        # Ejemplo (reemplaza por tu SQL real)
        # OJO: si tienes varias sentencias, sepáralas y ejecútalas en un bucle.
        c.execute("""
        -- AQUÍ TU SQL ACTUAL que consulta information_schema y hace los ALTER necesarios
        """)

def revert_relax_profesorado(apps, schema_editor):
    if schema_editor.connection.vendor != "mysql":
        return
    # Si tienes SQL de rollback, ponlo aquí; si no, déjalo no-op.

class Migration(migrations.Migration):
    dependencies = [
        # deja tu dependencia tal cual esté hoy (sin .py)
        ("academia_horarios", "0006_add_columns_to_comision"),
    ]
    operations = [
        migrations.RunPython(relax_profesorado, revert_relax_profesorado),
    ]

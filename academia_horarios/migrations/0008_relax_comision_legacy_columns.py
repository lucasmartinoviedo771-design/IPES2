# academia_horarios/migrations/0008_relax_comision_legacy_columns.py
from django.db import migrations

def relax_legacy_cols(apps, schema_editor):
    """
    Esta migración hace que las columnas 'anio' y 'materia_id' de la tabla
    'academia_horarios_comision' acepten valores NULL si existen y son NOT NULL.
    Esto se hace para flexibilizar la estructura de la tabla de cara a futuras
    refactorizaciones. La operación es idempotente y segura.
    """
    # Evita ejecutar este SQL en motores que no sean MySQL (ej. SQLite en CI)
    if schema_editor.connection.vendor != "mysql":
        return

    with schema_editor.connection.cursor() as c:
        # --- Lógica para la columna 'anio' ---
        c.execute("""
            SELECT IS_NULLABLE, COLUMN_TYPE
            FROM INFORMATION_SCHEMA.COLUMNS
            WHERE TABLE_SCHEMA = DATABASE()
              AND TABLE_NAME = 'academia_horarios_comision'
              AND COLUMN_NAME = 'anio'
        """)
        row = c.fetchone()
        if row:
            is_nullable, coltype = row
            if is_nullable == 'NO':
                c.execute(f"""
                    ALTER TABLE `academia_horarios_comision`
                    MODIFY `anio` {coltype} NULL
                """)

        # --- Lógica para la columna 'materia_id' ---
        c.execute("""
            SELECT IS_NULLABLE, COLUMN_TYPE
            FROM INFORMATION_SCHEMA.COLUMNS
            WHERE TABLE_SCHEMA = DATABASE()
              AND TABLE_NAME = 'academia_horarios_comision'
              AND COLUMN_NAME = 'materia_id'
        """)
        row = c.fetchone()
        if row:
            is_nullable, coltype = row
            if is_nullable == 'NO':
                c.execute(f"""
                    ALTER TABLE `academia_horarios_comision`
                    MODIFY `materia_id` {coltype} NULL
                """)


class Migration(migrations.Migration):
    dependencies = [
        # Asegúrate de que este es el nombre correcto de tu migración anterior
        ("academia_horarios", "0007_relax_comision_profesorado"),
    ]

    operations = [
        # Ejecuta la función para aplicar los cambios.
        # La función de reverso es no-op (no hace nada), lo cual es seguro
        # para este tipo de cambio que relaja una restricción.
        migrations.RunPython(relax_legacy_cols, migrations.RunPython.noop),
    ]

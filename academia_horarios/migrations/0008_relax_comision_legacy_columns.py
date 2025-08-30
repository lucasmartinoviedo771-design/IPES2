from django.db import migrations, connection

def relax_legacy_cols(apps, schema_editor):
    with connection.cursor() as c:
        # anio -> NULL si existe y es NOT NULL
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

        # materia_id -> NULL si existe y es NOT NULL (por si aparece luego)
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
        ("academia_horarios", "0007_relax_comision_profesorado"),  # ajustá si tu última es otra
    ]
    operations = [
        migrations.RunPython(relax_legacy_cols, migrations.RunPython.noop),
    ]

from django.db import migrations, connection

def relax_profesorado(apps, schema_editor):
    with connection.cursor() as c:
        # ¿Existe la columna 'profesorado' y es NOT NULL?
        c.execute("""
            SELECT IS_NULLABLE, COLUMN_TYPE
            FROM INFORMATION_SCHEMA.COLUMNS
            WHERE TABLE_SCHEMA = DATABASE()
              AND TABLE_NAME = 'academia_horarios_comision'
              AND COLUMN_NAME = 'profesorado'
        """)
        row = c.fetchone()
        if row:
            is_nullable, coltype = row  # ej: ('NO', 'varchar(255)')
            if is_nullable == 'NO':
                # La dejamos NULL preservando el tipo original
                c.execute(f"""
                    ALTER TABLE `academia_horarios_comision`
                    MODIFY `profesorado` {coltype} NULL
                """)

class Migration(migrations.Migration):
    dependencies = [
        ("academia_horarios", "0006_add_columns_to_comision"),  # usa tu última migración real
    ]
    operations = [
        migrations.RunPython(relax_profesorado, migrations.RunPython.noop),
    ]

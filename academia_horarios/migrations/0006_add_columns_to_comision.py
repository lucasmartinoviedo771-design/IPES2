from django.db import migrations, connection

def add_missing_columns(apps, schema_editor):
    with connection.cursor() as cursor:
        # A) Agregar columna materia_en_plan_id si falta
        cursor.execute("""
            SELECT COUNT(*)
            FROM information_schema.COLUMNS
            WHERE TABLE_SCHEMA = DATABASE()
              AND TABLE_NAME = 'academia_horarios_comision'
              AND COLUMN_NAME = 'materia_en_plan_id'
        """)
        (exists_mep_col,) = cursor.fetchone()
        if not exists_mep_col:
            cursor.execute("""
                ALTER TABLE `academia_horarios_comision`
                ADD COLUMN `materia_en_plan_id` INT NULL AFTER `id`;
            """)

        # B) Agregar columna periodo_id si falta (por las dudas)
        cursor.execute("""
            SELECT COUNT(*)
            FROM information_schema.COLUMNS
            WHERE TABLE_SCHEMA = DATABASE()
              AND TABLE_NAME = 'academia_horarios_comision'
              AND COLUMN_NAME = 'periodo_id'
        """)
        (exists_per_col,) = cursor.fetchone()
        if not exists_per_col:
            cursor.execute("""
                ALTER TABLE `academia_horarios_comision`
                ADD COLUMN `periodo_id` INT NULL AFTER `materia_en_plan_id`;
            """)

        # C) Índices (opcionales, pero útiles). Crear solo si faltan.
        cursor.execute("""
            SELECT COUNT(*)
            FROM information_schema.STATISTICS
            WHERE TABLE_SCHEMA = DATABASE()
              AND TABLE_NAME = 'academia_horarios_comision'
              AND INDEX_NAME = 'comision_mep_idx'
        """)
        (exists_idx_mep,) = cursor.fetchone()
        if not exists_idx_mep:
            cursor.execute("""
                CREATE INDEX `comision_mep_idx`
                ON `academia_horarios_comision` (`materia_en_plan_id`);
            """)

        cursor.execute("""
            SELECT COUNT(*)
            FROM information_schema.STATISTICS
            WHERE TABLE_SCHEMA = DATABASE()
              AND TABLE_NAME = 'academia_horarios_comision'
              AND INDEX_NAME = 'comision_periodo_idx'
        """)
        (exists_idx_per,) = cursor.fetchone()
        if not exists_idx_per:
            cursor.execute("""
                CREATE INDEX `comision_periodo_idx`
                ON `academia_horarios_comision` (`periodo_id`);
            """)

class Migration(migrations.Migration):
    dependencies = [
        ("academia_horarios", "0005_add_profesorados_column_to_plan"),
    ]
    operations = [
        migrations.RunPython(add_missing_columns, migrations.RunPython.noop),
    ]

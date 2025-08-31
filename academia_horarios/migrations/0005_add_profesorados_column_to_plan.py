# academia_horarios/migrations/0005_add_profesorados_column_to_plan.py
from django.db import migrations

TABLE = "academia_horarios_plan"
COLUMN = "profesorados"

# Ajustá el tipo si en MySQL usabas otro (ej.: TEXT, LONGTEXT, JSON, etc.)
MYSQL_ALTER_ADD = f"ALTER TABLE {TABLE} ADD COLUMN {COLUMN} LONGTEXT NULL;"
MYSQL_ALTER_DROP = f"ALTER TABLE {TABLE} DROP COLUMN {COLUMN};"

def add_profesorados_column(apps, schema_editor):
    vendor = schema_editor.connection.vendor
    if vendor != "mysql":
        # En SQLite (y otros) no hacemos nada: la tabla no existe en CI.
        return

    with schema_editor.connection.cursor() as cursor:
        cursor.execute(
            """
            SELECT 1
            FROM information_schema.COLUMNS
            WHERE TABLE_SCHEMA = DATABASE()
              AND TABLE_NAME = %s
              AND COLUMN_NAME = %s
            """,
            [TABLE, COLUMN],
        )
        exists = cursor.fetchone() is not None

    if not exists:
        schema_editor.execute(MYSQL_ALTER_ADD)

def remove_profesorados_column(apps, schema_editor):
    vendor = schema_editor.connection.vendor
    if vendor != "mysql":
        return
    # Si no existe, MySQL tiraría error; podés envolver con try si querés.
    schema_editor.execute(MYSQL_ALTER_DROP)

class Migration(migrations.Migration):
    dependencies = [
        # ⚠️ Usa aquí el nombre EXACTO (sin .py) de tu 0004 (la que crea la tabla).
        ("academia_horarios", "0004_create_plan_table"),
    ]

    operations = [
        migrations.RunPython(add_profesorados_column, remove_profesorados_column),
    ]

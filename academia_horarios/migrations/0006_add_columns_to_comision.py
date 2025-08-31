# academia_horarios/migrations/0006_add_columns_to_comision.py
from django.db import migrations

TABLE = "academia_horarios_comision"

# ⚠️ COMPLETÁ ESTA LISTA con las columnas que agrega esta migración.
# Formato: (nombre_columna, definición_SQL_MySQL)
# Ejemplos:
#   ("turno", "VARCHAR(10) NULL"),
#   ("aula", "VARCHAR(100) NULL"),
#   ("capacidad", "INT NULL"),
COLUMNS_TO_ADD_MYSQL = [
    # ("columna", "TIPO NULL"),
]

def add_missing_columns(apps, schema_editor):
    vendor = schema_editor.connection.vendor
    if vendor != "mysql":
        # En SQLite/otros motores: no-op (evitamos usar information_schema.*)
        return

    with schema_editor.connection.cursor() as cursor:
        for col_name, col_def in COLUMNS_TO_ADD_MYSQL:
            # ¿Existe ya la columna?
            cursor.execute(
                """
                SELECT 1
                FROM information_schema.COLUMNS
                WHERE TABLE_SCHEMA = DATABASE()
                  AND TABLE_NAME = %s
                  AND COLUMN_NAME = %s
                """,
                [TABLE, col_name],
            )
            exists = cursor.fetchone() is not None
            if not exists:
                cursor.execute(f"ALTER TABLE {TABLE} ADD COLUMN {col_name} {col_def};")

def drop_columns(apps, schema_editor):
    vendor = schema_editor.connection.vendor
    if vendor != "mysql":
        return

    with schema_editor.connection.cursor() as cursor:
        for col_name, _ in COLUMNS_TO_ADD_MYSQL:
            # Si no existe, DROP fallaría; envolvemos en un try opcional
            try:
                cursor.execute(f"ALTER TABLE {TABLE} DROP COLUMN {col_name};")
            except Exception:
                pass

class Migration(migrations.Migration):
    dependencies = [
        # 👇 poné acá el nombre EXACTO (sin .py) de tu migración anterior
        ("academia_horarios", "0005_add_profesorados_column_to_plan"),
    ]

    operations = [
        migrations.RunPython(add_missing_columns, drop_columns),
    ]

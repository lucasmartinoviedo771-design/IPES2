# academia_horarios/migrations/0004_create_plan_table.py
from django.db import migrations

# ⚠️ Pega aquí el SQL real que ya usabas en MySQL para crear la tabla.
MYSQL_SQL = """
CREATE TABLE IF NOT EXISTS academia_horarios_plan (
    id BIGINT AUTO_INCREMENT PRIMARY KEY
    /* agrega aquí el resto de columnas EXACTAMENTE como en MySQL */
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
"""

DROP_SQL = "DROP TABLE IF EXISTS academia_horarios_plan;"

def forward(apps, schema_editor):
    # En CI usamos SQLite: no hacer nada ahí.
    if schema_editor.connection.vendor == "mysql":
        schema_editor.execute(MYSQL_SQL)

def backward(apps, schema_editor):
    # Si querés revertir solo en MySQL, dejalo así:
    if schema_editor.connection.vendor == "mysql":
        schema_editor.execute(DROP_SQL)
    else:
        # En SQLite la tabla no la creamos, pero no estorba ejecutar el DROP defensivo.
        schema_editor.execute(DROP_SQL)

class Migration(migrations.Migration):
    dependencies = [
        # 👉 Usa la dependencia real anterior (la que ya tenías en este archivo)
        ("academia_horarios", "0003_alter_comision_table_alter_docente_table_and_more"),
    ]

    operations = [
        migrations.RunPython(forward, backward),
    ]

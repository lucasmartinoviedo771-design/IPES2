from django.db import migrations, connection

def add_profesorados_column(apps, schema_editor):
    with connection.cursor() as cursor:
        # 1) Agregar columna profesorados_id si falta
        cursor.execute("""
            SELECT COUNT(*)
            FROM information_schema.COLUMNS
            WHERE TABLE_SCHEMA = DATABASE()
              AND TABLE_NAME = 'academia_horarios_plan'
              AND COLUMN_NAME = 'profesorados_id'
        """)
        (exists_col,) = cursor.fetchone()
        if not exists_col:
            cursor.execute("""
                ALTER TABLE `academia_horarios_plan`
                ADD COLUMN `profesorados_id` INT NULL AFTER `id`;
            """)

        # 2) Crear tabla academia_horarios_profesorado si no existe (opcional pero útil)
        cursor.execute("""
            SELECT COUNT(*)
            FROM information_schema.TABLES
            WHERE TABLE_SCHEMA = DATABASE()
              AND TABLE_NAME = 'academia_horarios_profesorado'
        """)
        (exists_table,) = cursor.fetchone()
        if not exists_table:
            cursor.execute("""
                CREATE TABLE `academia_horarios_profesorado` (
                  `id` INT NOT NULL AUTO_INCREMENT,
                  `nombre` VARCHAR(255) NOT NULL,
                  PRIMARY KEY (`id`),
                  UNIQUE KEY `profesorado_nombre_uniq` (`nombre`)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
            """)

        # 3) Crear índice si falta
        cursor.execute("""
            SELECT COUNT(*)
            FROM information_schema.STATISTICS
            WHERE TABLE_SCHEMA = DATABASE()
              AND TABLE_NAME = 'academia_horarios_plan'
              AND INDEX_NAME = 'plan_profesorados_id_idx'
        """)
        (exists_idx,) = cursor.fetchone()
        if not exists_idx:
            cursor.execute("""
                CREATE INDEX `plan_profesorados_id_idx`
                ON `academia_horarios_plan` (`profesorados_id`);
            """)

class Migration(migrations.Migration):
    dependencies = [
        ("academia_horarios", "0004_create_plan_table"),
    ]
    operations = [
        migrations.RunPython(add_profesorados_column, migrations.RunPython.noop),
    ]

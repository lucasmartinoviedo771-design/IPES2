from django.db import migrations

class Migration(migrations.Migration):
    dependencies = [
        ("academia_horarios", "0003_alter_comision_table_alter_docente_table_and_more"),
    ]

    operations = [
        migrations.RunSQL(
            """
            CREATE TABLE IF NOT EXISTS `academia_horarios_plan` (
              `id` int NOT NULL AUTO_INCREMENT,
              `nombre` varchar(255) NOT NULL,
              `codigo` varchar(64) NOT NULL DEFAULT '',
              PRIMARY KEY (`id`)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
            """
        ),
    ]

from django.db import migrations, models
from django.db.models import F, Q

class Migration(migrations.Migration):

    dependencies = [
        # La dependencia exacta que ya tenía tu archivo 0012
        ("academia_horarios", "0011_docente_dni"),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            # Dejamos esta sección vacía para no ejecutar comandos SQL
            # directamente, evitando así posibles errores de compatibilidad
            # con bases de datos como SQLite en entornos de prueba (CI).
            database_operations=[],

            # Aquí colocamos las operaciones originales. Esto actualiza el
            # "estado" de los modelos de Django para que sepa que el índice
            # y la restricción existen, lo cual es crucial para futuras
            # migraciones.
            state_operations=[
                migrations.AddIndex(
                    model_name="timeslot",
                    index=models.Index(
                        fields=["dia_semana", "inicio", "fin"],
                        name="academia_ho_dia_sem_cb4c98_idx",
                    ),
                ),
                migrations.AddConstraint(
                    model_name="timeslot",
                    constraint=models.CheckConstraint(
                        check=Q(inicio__lt=F("fin")),
                        name="timeslot_inicio_lt_fin",
                    ),
                ),
            ],
        ),
    ]

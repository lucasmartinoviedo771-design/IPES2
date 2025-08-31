from django.db import migrations, models
from django.db.models import Q, F

class Migration(migrations.Migration):

    dependencies = [
        ("academia_horarios", "0011_NOMBRE_REAL_DE_TU_MIGRACION"),  # ← reemplazar por el tuyo
    ]

    operations = [
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
    ]

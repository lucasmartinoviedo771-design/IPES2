# academia_horarios/migrations/000X_*.py  (el que tenía el AddIndex a TimeSlot)
from django.db import migrations

class Migration(migrations.Migration):
    dependencies = [
        ("academia_horarios", "0001_initial"),   # deja las que ya estuvieran
        # ... si había más, mantenelas
    ]
    # El índice sobre TimeSlot se salta porque la tabla no existe en este punto / el modelo cambió
    operations = []

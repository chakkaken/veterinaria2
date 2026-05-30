from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Componentes', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelTable(
            name='usuario',
            table='Componentes_usuario',
        ),
    ]

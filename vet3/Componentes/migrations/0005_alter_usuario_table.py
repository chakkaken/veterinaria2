from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('Componentes', '0004_usuario_is_verified_verificationtoken'),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            state_operations=[
                migrations.AlterModelTable(
                    name='usuario',
                    table='componentes_usuario',
                ),
            ],
            database_operations=[],
        ),
    ]

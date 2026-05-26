from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('Componentes', '0003_remove_mascotas_correo_mascotas_especie_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='usuario',
            name='is_verified',
            field=models.BooleanField(default=False, verbose_name='Email verificado'),
        ),
        migrations.CreateModel(
            name='VerificationToken',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('token', models.CharField(max_length=64, unique=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('expires_at', models.DateTimeField()),
                ('usuario', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='verification_tokens', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Token de verificación',
                'verbose_name_plural': 'Tokens de verificación',
            },
        ),
    ]

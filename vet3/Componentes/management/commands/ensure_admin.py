from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

Usuario = get_user_model()


class Command(BaseCommand):
    help = 'Crea o actualiza el usuario administrador por defecto'

    def handle(self, *args, **options):
        username = 'admin'
        password = 'admin123'
        email = options.get('email', '')

        usuario, created = Usuario.objects.update_or_create(
            username=username,
            defaults={
                'email': email,
                'rol': 'admin',
                'is_staff': True,
                'is_superuser': True,
                'is_active': True,
                'is_verified': True,
            }
        )

        usuario.set_password(password)
        usuario.save()

        if created:
            self.stdout.write(self.style.SUCCESS(f'Admin user "{username}" created successfully'))
        else:
            self.stdout.write(self.style.SUCCESS(f'Admin user "{username}" updated successfully'))

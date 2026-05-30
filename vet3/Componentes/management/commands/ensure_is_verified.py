from django.core.management.base import BaseCommand
from django.db import connection
from django.core.management import call_command
import logging


class Command(BaseCommand):
    help = 'Ensure the is_verified column exists on Componentes.Usuario. Attempts to run migrations, falls back to ALTER TABLE.'

    def handle(self, *args, **options):
        logger = logging.getLogger(__name__)
        table = 'componentes_usuario'

        # Check if column exists
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT column_name FROM information_schema.columns WHERE table_name=%s AND column_name=%s",
                [table, 'is_verified'],
            )
            row = cursor.fetchone()

        if row:
            self.stdout.write(self.style.SUCCESS('Column is_verified already exists on %s' % table))
            return

        self.stdout.write('Column is_verified not found; attempting to run migrations for app "Componentes"...')
        try:
            call_command('migrate', 'Componentes', verbosity=1, interactive=False)
            self.stdout.write(self.style.SUCCESS('Migrations applied. Please verify the column exists.'))
            return
        except Exception as e:
            logger.exception('migrate Componentes failed: %s', e)
            self.stderr.write('migrate failed: %s' % e)

        # Fallback: try to add column directly (Postgres/SQL compatible)
        self.stdout.write('Attempting to add column via ALTER TABLE...')
        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    f'ALTER TABLE "{table}" ADD COLUMN is_verified boolean DEFAULT false NOT NULL;'
                )
            self.stdout.write(self.style.SUCCESS('Column is_verified added via ALTER TABLE.'))
        except Exception as e2:
            logger.exception('Failed to add column via ALTER TABLE: %s', e2)
            self.stderr.write('Failed to add column via ALTER TABLE: %s' % e2)
            raise

from .settings import *

# Use in-memory SQLite for tests to avoid external DB/SSL issues
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}

# Use console email backend during tests
EMAIL_BACKEND = 'django.core.mail.backends.locmem.EmailBackend'

# Disable migrations for Componentes during tests to avoid DB-specific SQL
MIGRATION_MODULES = {
    'Componentes': None,
}

# Use simple staticfiles storage in tests to avoid manifest lookup errors
STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.StaticFilesStorage'
STORAGES = {
    'staticfiles': {
        'BACKEND': 'django.contrib.staticfiles.storage.StaticFilesStorage',
    }
}

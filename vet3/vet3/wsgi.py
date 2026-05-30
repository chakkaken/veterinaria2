"""
WSGI config for vet3 project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/howto/deployment/wsgi/
"""

import os
import logging

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'vet3.vet3.settings')

logger = logging.getLogger(__name__)

try:
	application = get_wsgi_application()
	# Quick DB connection check to surface DB config errors at startup
	try:
		from django.db import connections
		conn = connections['default']
		conn.ensure_connection()
		logger.info('Database connection successful on startup')
	except Exception as db_exc:
		# Log a masked DATABASE_URL (hide password) to aid debugging
		try:
			db_url = os.environ.get('DATABASE_URL', '')
			masked = db_url
			if db_url:
				# naive mask: replace :password@ with :***@
				import re
				masked = re.sub(r':[^:@]+@', ':***@', db_url)
			logger.error('DATABASE_URL (masked): %s', masked)
		except Exception:
			logger.exception('Failed to mask DATABASE_URL')
		logger.exception('Database connection failed during WSGI startup: %s', db_exc)
		# Re-raise so the process fails loudly and Render returns server error with logs
		raise
except Exception as exc:
	logger.exception('Failed to initialize WSGI application: %s', exc)
	raise

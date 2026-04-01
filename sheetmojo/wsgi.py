"""
WSGI config for sheetmojo project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/howto/deployment/wsgi/
"""

import os
from pathlib import Path

from django.core.wsgi import get_wsgi_application
from .env import load_env_file

load_env_file(Path(__file__).resolve().parent.parent / '.env')

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sheetmojo.settings')

application = get_wsgi_application()

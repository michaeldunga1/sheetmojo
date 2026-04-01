"""PythonAnywhere WSGI configuration for SheetMojo.

Copy the contents of this file into your PythonAnywhere WSGI file:
  /var/www/dunga_pythonanywhere_com_wsgi.py

Then click "Reload" in the PythonAnywhere Web tab.
"""

import os
import sys
from pathlib import Path

# Absolute project path on PythonAnywhere.
PROJECT_HOME = Path('/home/dunga/sheetmojo')

# Ensure project package imports work.
if str(PROJECT_HOME) not in sys.path:
    sys.path.insert(0, str(PROJECT_HOME))

# Load environment variables from .env if present.
# This uses the same lightweight loader already used by manage.py and wsgi.py.
try:
    from sheetmojo.env import load_env_file
    load_env_file(PROJECT_HOME / '.env')
except Exception:
    # Do not fail app startup if .env is missing; env vars may be set elsewhere.
    pass

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sheetmojo.settings')

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()

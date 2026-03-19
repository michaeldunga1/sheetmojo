# SheetMojo

Multi-topic Django calculator project with domain apps (algebra, calculus, geometry, physics, and more).

## Local setup

1. Create and activate a virtual environment.
2. Install dependencies.
3. Run migrations.
4. Start the dev server.

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

## Environment variables

Copy values from `.env.example` into your shell or hosting provider configuration.

- `DJANGO_DEBUG`: `1` for local development, `0` for production.
- `DJANGO_SECRET_KEY`: required in production.
- `DJANGO_ALLOWED_HOSTS`: comma-separated hosts allowed by Django.
- `DJANGO_CSRF_TRUSTED_ORIGINS`: optional comma-separated HTTPS origins.
- `DATABASE_URL`: optional; defaults to SQLite `db.sqlite3` if omitted.

## Deploy to PythonAnywhere

### 1. Clone from GitHub on PythonAnywhere

Use a Bash console on PythonAnywhere:

```bash
git clone git@github.com:michaeldunga1/sheetmojo.git
cd sheetmojo
```

### 2. Create virtualenv and install dependencies

```bash
mkvirtualenv --python=/usr/bin/python3.10 sheetmojo-venv
workon sheetmojo-venv
pip install -r requirements.txt
```

Use any Python version available on your PythonAnywhere account that is compatible with your pinned dependencies.

### 3. Create web app (Manual configuration)

In PythonAnywhere Web tab:

1. Add a new web app.
2. Choose `Manual configuration`.
3. Select Python version matching your virtualenv.
4. Set virtualenv path to `/home/<username>/.virtualenvs/sheetmojo-venv`.
5. Set source and working directory to `/home/<username>/sheetmojo`.

### 4. Configure environment variables (Web tab)

Set at least:

- `DJANGO_DEBUG=0`
- `DJANGO_SECRET_KEY=<strong-random-value>`
- `DJANGO_ALLOWED_HOSTS=<username>.pythonanywhere.com`
- `DJANGO_CSRF_TRUSTED_ORIGINS=https://<username>.pythonanywhere.com`

### 5. Edit PythonAnywhere WSGI file

Edit the WSGI file linked from your web app (for example `/var/www/<username>_pythonanywhere_com_wsgi.py`):

```python
import os
import sys

path = '/home/<username>/sheetmojo'
if path not in sys.path:
	sys.path.insert(0, path)

os.environ['DJANGO_SETTINGS_MODULE'] = 'sheetmojo.settings'

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
```

### 6. Run migrations and collect static files

```bash
workon sheetmojo-venv
cd ~/sheetmojo
python manage.py migrate
python manage.py collectstatic --noinput
```

### 7. Reload web app

Click `Reload` on the PythonAnywhere Web tab after each deployment.

## Ongoing deploy workflow

After pushing to GitHub:

```bash
cd ~/sheetmojo
git pull
workon sheetmojo-venv
pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic --noinput
```

Then reload the web app from the Web tab.

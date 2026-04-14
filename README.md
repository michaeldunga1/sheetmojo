# SheetMojo

A Django app for posts, channels, profiles, comments, and follows.

## 1. Local Development Setup

### Prerequisites

- Python 3.10+
- `pip`

### Steps

1. Create and activate a virtual environment:

```bash
python -m venv venv
source venv/bin/activate
```

1. Install dependencies:

```bash
pip install -r requirements.txt
```

1. Create local environment file:

```bash
cp .env.example .env
```

1. Update `.env` for local dev (defaults already work):

```env
DJANGO_DEBUG=True
DJANGO_ALLOWED_HOSTS=127.0.0.1,localhost
DJANGO_DB_ENGINE=django.db.backends.sqlite3
DJANGO_DB_NAME=db.sqlite3
```

1. Run migrations and create an admin user:

```bash
python manage.py migrate
python manage.py createsuperuser
```

1. Start development server:

```bash
python manage.py runserver
```

## 2. Production Deployment on PythonAnywhere

### 2.1 Upload code

1. Create a PythonAnywhere account.
1. Open a Bash console.
1. Clone your repository into your home directory.

### 2.2 Create virtualenv and install packages

```bash
mkvirtualenv --python=/usr/bin/python3.10 sheetmojo-env
workon sheetmojo-env
cd ~/sheetmojo
pip install -r requirements.txt
```

### 2.3 Configure environment variables

Create a `.env` file in your project root (`~/sheetmojo/.env`) with production values:

```env
DJANGO_SECRET_KEY=use-a-strong-random-value
DJANGO_DEBUG=False
DJANGO_ALLOWED_HOSTS=yourusername.pythonanywhere.com
DJANGO_CSRF_TRUSTED_ORIGINS=https://yourusername.pythonanywhere.com

# If using MySQL on PythonAnywhere:
DJANGO_DB_ENGINE=django.db.backends.mysql
DJANGO_DB_NAME=yourusername$sheetmojo
DJANGO_DB_USER=yourusername
DJANGO_DB_PASSWORD=your-db-password
DJANGO_DB_HOST=yourusername.mysql.pythonanywhere-services.com
DJANGO_DB_PORT=3306
```

### 2.4 Run Django management commands

```bash
workon sheetmojo-env
cd ~/sheetmojo
python manage.py migrate
python manage.py collectstatic --noinput
python manage.py createsuperuser
```

### 2.5 Create and configure the PythonAnywhere web app

1. Go to **Web** tab -> **Add a new web app**.
1. Choose **Manual configuration** and Python 3.10.
1. Set **Virtualenv** to:

```text
/home/yourusername/.virtualenvs/sheetmojo-env
```

1. Set **Source code** to:

```text
/home/yourusername/sheetmojo
```

1. Configure static and media mappings in Web tab:

- URL `/static/` -> Directory `/home/yourusername/sheetmojo/staticfiles`
- URL `/media/` -> Directory `/home/yourusername/sheetmojo/media`

### 2.6 Update WSGI file on PythonAnywhere

In the PythonAnywhere-generated WSGI config file:

1. Add project path to `sys.path`.
1. Set `DJANGO_SETTINGS_MODULE=sheetmojo.settings`.
1. Point to `sheetmojo/wsgi.py` application object.

Example core lines (adjust username/path):

```python
import os
import sys

path = '/home/yourusername/sheetmojo'
if path not in sys.path:
    sys.path.append(path)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sheetmojo.settings')

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
```

### 2.7 Reload and verify

1. Click **Reload** in the Web tab.
1. Open `https://yourusername.pythonanywhere.com`.
1. Check **Error log** if anything fails.

### 2.8 GitHub -> PythonAnywhere deployment routine

Use this routine whenever you push changes to GitHub and want to deploy on PythonAnywhere.

#### First-time setup from GitHub

```bash
# In PythonAnywhere Bash console
cd ~
git clone https://github.com/<your-github-username>/sheetmojo.git
cd sheetmojo

mkvirtualenv --python=/usr/bin/python3.10 sheetmojo-env
workon sheetmojo-env
pip install -r requirements.txt

# Then configure ~/sheetmojo/.env and Web tab settings as described above.
python manage.py migrate
python manage.py collectstatic --noinput
```

#### Repeat deployment after each GitHub push

```bash
# In PythonAnywhere Bash console
workon sheetmojo-env
cd ~/sheetmojo

git fetch origin
git checkout main
git pull origin main

pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic --noinput
```

Then in the **PythonAnywhere Web tab**:

1. Click **Reload**.
1. Open your site and verify key pages.
1. If needed, inspect **Error log** and **Server log**.

Optional quick health check command:

```bash
workon sheetmojo-env
cd ~/sheetmojo
python manage.py check
```

#### Optional one-command deploy script

This repo includes `deploy_pa.sh` to run the repeat deployment routine automatically:

```bash
cd ~/sheetmojo
./deploy_pa.sh
```

Use a custom branch if needed:

```bash
./deploy_pa.sh main
```

After the script completes, click **Reload** in the PythonAnywhere **Web** tab.

## 3. Settings Summary

The app now supports environment-based configuration:

- `DJANGO_DEBUG`
- `DJANGO_SECRET_KEY`
- `DJANGO_ALLOWED_HOSTS`
- `DJANGO_CSRF_TRUSTED_ORIGINS`
- `DJANGO_DB_ENGINE`, `DJANGO_DB_NAME`, `DJANGO_DB_USER`, `DJANGO_DB_PASSWORD`, `DJANGO_DB_HOST`, `DJANGO_DB_PORT`
- `DJANGO_SESSION_COOKIE_SECURE`, `DJANGO_CSRF_COOKIE_SECURE`, `DJANGO_SECURE_SSL_REDIRECT`, `DJANGO_SECURE_HSTS_*`

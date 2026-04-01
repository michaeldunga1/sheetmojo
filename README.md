# sheetmojo

SheetMojo is a Django business directory and user listing app.

## Deploy To PythonAnywhere

### 1. Create virtual environment and install dependencies

```bash
mkvirtualenv --python=/usr/bin/python3.12 sheetmojo-venv
cd ~/sheetmojo
pip install -r requirements.txt
```

### 2. Configure environment variables

Copy the example file and edit values:

```bash
cp .env.pythonanywhere.example .env
```

Set these values in `.env`:

- `DJANGO_SECRET_KEY`: strong random secret
- `DJANGO_DEBUG=False`
- `DJANGO_ALLOWED_HOSTS=127.0.0.1,localhost,::1,pythonanywhere.com,.pythonanywhere.com,<your-username>.pythonanywhere.com`
- `DJANGO_CSRF_TRUSTED_ORIGINS=https://*.pythonanywhere.com,https://<your-username>.pythonanywhere.com`
- `DJANGO_SECURE_SSL_REDIRECT=True`

### 3. Run migrations and collect static files

```bash
python manage.py migrate
python manage.py collectstatic --noinput
python manage.py check
```

### 4. Configure PythonAnywhere web app

In the Web tab:

- Set source code path to `/home/<your-username>/sheetmojo`
- Set virtualenv to `/home/<your-username>/.virtualenvs/sheetmojo-venv`
- Configure static files mapping:
	- URL: `/static/`
	- Directory: `/home/<your-username>/sheetmojo/staticfiles`

### 5. Configure WSGI

Use the prepared template in `pythonanywhere_wsgi.py` and paste it into your PythonAnywhere WSGI file, then reload the web app.

Default WSGI path on PythonAnywhere:

- `/var/www/<your-username>_pythonanywhere_com_wsgi.py`

### 6. Reload app

Click **Reload** in PythonAnywhere Web tab.

## Optional: create admin user

```bash
python manage.py createsuperuser
```

## PythonAnywhere Troubleshooting

### 1. Static files not loading (CSS/JS missing)

Symptoms:

- Page renders without styling.

Fix:

1. Run:

```bash
python manage.py collectstatic --noinput
```

2. In PythonAnywhere Web tab, confirm static mapping:

- URL: `/static/`
- Directory: `/home/<your-username>/sheetmojo/staticfiles`

3. Reload the web app.

### 2. `DisallowedHost` error

Symptoms:

- Error says invalid `HTTP_HOST` header.

Fix:

Ensure `.env` contains your exact host in `DJANGO_ALLOWED_HOSTS`, for example:

`DJANGO_ALLOWED_HOSTS=127.0.0.1,localhost,::1,pythonanywhere.com,.pythonanywhere.com,<your-username>.pythonanywhere.com`

Then reload the web app.

### 3. CSRF verification failed on login/forms

Symptoms:

- POST requests fail with CSRF error.

Fix:

Ensure `.env` includes your domain in `DJANGO_CSRF_TRUSTED_ORIGINS`, for example:

`DJANGO_CSRF_TRUSTED_ORIGINS=https://*.pythonanywhere.com,https://<your-username>.pythonanywhere.com`

Then reload the web app.

### 4. App fails to start (`ModuleNotFoundError`)

Symptoms:

- WSGI/log file shows missing package/module.

Fix:

1. Activate the correct virtualenv and reinstall dependencies:

```bash
workon sheetmojo-venv
cd ~/sheetmojo
pip install -r requirements.txt
```

2. Confirm Web tab uses the same virtualenv path.

3. Reload the web app.

### 5. Database errors after deploy (`no such table`)

Symptoms:

- Requests fail with missing-table errors.

Fix:

```bash
python manage.py migrate
```

Then reload the web app.

### 6. How to inspect errors quickly

Use PythonAnywhere logs:

- Error log: Web tab -> **Error log**
- Server log: Web tab -> **Server log**

After each fix, always click **Reload**.

## Post-Deploy Smoke Test Checklist

Run this quick checklist after each deploy:

1. Open `/` and confirm business list renders with CSS styling.
2. Open `/countries/` and confirm countries load and search works.
3. Open `/login/` and `/register/` and confirm pages load without CSRF errors.
4. Sign in and open `/add-business/`; submit a test listing and verify redirect success.
5. Open one business detail page and verify location links and metadata render correctly.

Optional shell checks:

```bash
python manage.py check
python manage.py showmigrations | tail -n 20
```

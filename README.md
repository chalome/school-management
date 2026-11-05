# Petit Enfant Grand Cœur

A Django-based management portal for the Petit Enfant Grand Cœur crèche and
maternelle in Burundi. It manages classrooms, staff, children and their
contacts, and monthly fee payments.

## Features

- Staff authentication, profiles, password changes, and password recovery.
- Classroom and teacher records.
- Child registration, family and pickup contacts, and medical information.
- Monthly fees, partial payments, penalties, transaction references, and
  receipts in Burundian francs (Fbu).

All management pages require a signed-in user. Accounts are created by an
administrator; there is no public signup. Fine-grained staff permissions have
not been implemented, so signed-in staff currently share access to management
pages. Review access controls before using real student or health records.

See [project_documentation.md](project_documentation.md) for the data model,
page URLs, and additional project details.

## Requirements

- Python 3.12 or newer (required by the pinned Django 6.1 release).
- Packages listed in `requirements.txt`.

## Local setup

From the project directory:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Open `http://127.0.0.1:8000/accounts/login/` to sign in. Uploaded photos and
payment proof files are stored under `media/`. Password-reset messages use
Django's console email backend by default; configure a real email backend to
send email outside local development.

## Checks and tests

```bash
python manage.py check
python manage.py makemigrations --check --dry-run
python manage.py test accounts core children teachers payments
```

## PythonAnywhere deployment

Use PythonAnywhere's **Manual Configuration** for a new web app and select
Python 3.12 or newer. The pinned Django version requires it. Follow
PythonAnywhere's guide for [deploying an existing Django project](https://help.pythonanywhere.com/pages/DeployExistingDjangoProject/).

Before making the site public, configure production settings securely:

- Set a new, private `SECRET_KEY` through the deployment environment; do not
  reuse the development key or commit production secrets.
- Set `DEBUG=False` and `ALLOWED_HOSTS` to the actual site hostname(s).
- Configure HTTPS and secure cookies. Enable HSTS only after HTTPS is working.
- Set `STATIC_ROOT`, run `python manage.py collectstatic`, and map `/static/`
  to that directory in the PythonAnywhere Web tab.
- Configure email settings if password recovery should send real messages.

The current settings are development-oriented: `DEBUG` is enabled,
`ALLOWED_HOSTS` is empty, the secret key is hard-coded, and `STATIC_ROOT` is
not configured. The app is therefore **not ready for public production
deployment** until these settings are addressed.

## School years

The application starts with an active school year using a September 1–June 30
calendar. In Django admin, add school years and adjust their start/end dates if
the school calendar changes; a new year's dates default to one year after the
active year's dates. Mark the intended year active in admin. The navigation
dropdown starts on that active year and lets staff switch the children,
classroom counts, dashboard, and payments to another year. The selection is
remembered for that staff session.

Child identity, family, and health details are kept on the child's permanent
record. Enrollment and classroom assignment are stored separately per school
year, and each payment is associated with a school year. Existing child
assignments are migrated into the active year; existing payments are assigned
using their recorded month when possible.

Then, in a PythonAnywhere Bash console, install requirements in the web app's
virtual environment and run database migrations:

```bash
python -m pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
```

The SQLite database and uploaded files are excluded from Git. If migrating an
existing installation, transfer the database and `media/` files separately,
store them in persistent locations, and configure backups and a PythonAnywhere
media-file mapping. Otherwise, the deployment starts with a new database.

After configuration, set the web app's source and working directory to the
folder containing `manage.py`, point its WSGI configuration at `main.wsgi`,
configure static and (if needed) media mappings in the Web tab, then reload
the app.

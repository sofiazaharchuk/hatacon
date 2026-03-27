# Django PUB Hackathon Project

Two-factor authentication for Django:
1. Step 1: email and password.
2. Step 2: ECP verification using uploaded signature, certificate, and signed data.

The project includes:
- Django app with user registration/login dashboard flow.
- Local package `django_ecp_auth` integrated as Django authentication backend.
- Docker setup with PostgreSQL.
- Packaging metadata for PyPI (`pyproject.toml`).

## Tech Stack

- Python 3.12+
- Django 6.0+
- Jinja2
- PostgreSQL
- Docker / Docker Compose
- cryptography
- pycryptodome
- asn1crypto
- certvalidator

## Local Run (without Docker)

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

## Docker Run

```bash
make build
make up
make migrate
```

Open: `http://localhost:8000`

## Environment Variables

Create and edit:
- `environment/backend.env`
- `environment/postgresql.env`

Required backend variables:
- `DJANGO_SECRET_KEY`
- `DEBUG`
- `ALLOWED_HOSTS`
- `DATABASE_URL`
- `ECP_TRUSTED_CA_CERTS`

## ECP Configuration

`backend/settings.py` uses:

```python
ECP_AUTH = {
    'TRUSTED_CA_CERTS': os.environ.get('ECP_TRUSTED_CA_CERTS', ''),
    'CERT_VALIDATION_ENABLED': False,
    'USER_MODEL_FIELD': 'username',
    'AUTO_CREATE_USER': False,
    'LOGIN_TEMPLATE': 'auth/ecp_login.html',
    'REQUIRE_STEP1_SESSION': True,
}
```

For stricter validation in production:
- set `CERT_VALIDATION_ENABLED=True`
- set `ECP_TRUSTED_CA_CERTS` to a real CA bundle path in the container

## Security Notes

- Private key is never stored in the database.
- Private key is provided as a one-time downloadable `.pem` file.
- The download response sets `Content-Disposition: attachment` and no-cache headers.
- ECP step requires session from the first login step.

## Tests

```bash
python manage.py check
python manage.py test templates.users
```

## Packaging

Build package:

```bash
python -m pip install --upgrade build
python -m build
```

Publish:

```bash
python -m pip install --upgrade twine
python -m twine upload dist/*
```

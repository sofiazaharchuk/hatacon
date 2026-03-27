# Deploy Checklist

## 1. Prepare server

- Install Docker and Docker Compose plugin.
- Copy the project to server.
- Open port `8000` in firewall or map to reverse proxy.

## 2. Configure environment

Update files:
- `environment/backend.env`
- `environment/postgresql.env`

Production values:
- `DEBUG=False`
- `ALLOWED_HOSTS=your-domain.com,server-ip`
- `DJANGO_SECRET_KEY=<strong-random-value>`
- `DATABASE_URL=postgresql://django_user:django_password@db:5432/django_db`
- `ECP_TRUSTED_CA_CERTS=/app/environment/ca_bundle.pem`

Replace `environment/ca_bundle.pem` with your trusted CA chain.

## 3. Build and run

```bash
make build
make up
make migrate
```

## 4. Smoke tests

```bash
make check
make test
```

Manual checks:
- open `/register/`
- create test user and download private key file
- open `/login/` and finish step 1
- open `/ecp/login/` and submit signature files
- confirm redirect to `/dashboard/`

## 5. Optional package publishing

```bash
python -m pip install --upgrade build twine
python -m build
python -m twine upload dist/*
```

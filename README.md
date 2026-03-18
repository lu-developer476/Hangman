# Ahorcado Retro Toon

Proyecto del juego **Ahorcado** hecho con **Python + Django**, preparado para **Render** y con una estética **minimalista caricaturesca inspirada en los 80/90**.

## Stack

- Python 3.13
- Django 5.2.12
- Gunicorn
- WhiteNoise
- PostgreSQL en Render

## Lo que ya viene resuelto

- Configuración productiva para Render.
- `gunicorn` listo en `requirements.txt`.
- `WhiteNoise` para servir archivos estáticos sin inventos raros.
- `DATABASE_URL` para PostgreSQL.
- `render.yaml` para crear el servicio web y la base en Render.
- `healthCheckPath` en `/health/`.
- `build.sh` para instalar dependencias, correr `collectstatic` y ejecutar migraciones.
- Fallback local con SQLite para probar sin PostgreSQL.

## Comandos reales de Render

### Build Command

```bash
./build.sh
```

### Start Command

```bash
gunicorn ahorcado.wsgi:application
```

Sí, **gunicorn**. No hay misterio. Si no está en `requirements.txt`, Render te escupe un `command not found` y te arruina el deploy.

## Variables de entorno reales para el despliegue

### Mínimas

- `PYTHON_VERSION=3.13.2`
- `SECRET_KEY=<tu_clave_secreta>`
- `DEBUG=false`
- `ALLOWED_HOSTS=.onrender.com`
- `CSRF_TRUSTED_ORIGINS=https://*.onrender.com`
- `DATABASE_URL=<connectionString de tu Render Postgres>`

### Recomendadas si usás dominio custom

- `ALLOWED_HOSTS=.onrender.com,tudominio.com,www.tudominio.com`
- `CSRF_TRUSTED_ORIGINS=https://*.onrender.com,https://tudominio.com,https://www.tudominio.com`

## Deploy recomendado: con `render.yaml`

El repo ya trae un `render.yaml` que define:

- una base PostgreSQL llamada `ahorcado-db`
- un web service llamado `ahorcado-django`
- `buildCommand`
- `startCommand`
- variables de entorno
- `healthCheckPath`

Con eso evitás el clásico festival de errores manuales.

## Deploy manual en Render

1. Crear un **PostgreSQL** en Render.
2. Crear un **Web Service** desde el repo.
3. Usar:
   - **Build Command:** `./build.sh`
   - **Start Command:** `gunicorn ahorcado.wsgi:application`
4. Cargar las variables de entorno.
5. Pegar el `connectionString` del Postgres en `DATABASE_URL`.

## Correr local

```bash
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
# o .venv\Scripts\activate en Windows
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

## Health check

- Endpoint: `/health/`
- Respuesta esperada: `ok`

## Notas importantes

- En producción, los archivos estáticos los sirve **WhiteNoise**.
- El proyecto usa `signed_cookies` para sesión del juego, así que el gameplay no depende del motor de sesión en base de datos.
- Igual se ejecutan migraciones porque Django sigue necesitando consistencia si después querés usar admin, auth o cualquier otra cosa seria.

## Estructura

```text
ahorcado_render_project/
├── ahorcado/
├── app/
├── build.sh
├── manage.py
├── render.yaml
├── requirements.txt
└── README.md
```

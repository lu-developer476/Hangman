# Ahorcado Retro Toon

![Python](https://img.shields.io/badge/Python-3.13-3776AB?logo=python&logoColor=white)
![Django](https://img.shields.io/badge/Django-5.2.12-092E20?logo=django&logoColor=white)
![Gunicorn](https://img.shields.io/badge/Gunicorn-23.0.0-499848?logo=gunicorn&logoColor=white)
![WhiteNoise](https://img.shields.io/badge/WhiteNoise-6.9.0-ffffff?logo=django&logoColor=092E20)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-Render-4169E1?logo=postgresql&logoColor=white)
![Render](https://img.shields.io/badge/Deploy-Render-46E3B7?logo=render&logoColor=000000)
![Tests](https://img.shields.io/badge/tests-Django%20TestCase-success)

Juego web de **Ahorcado** hecho con **Python + Django**, desplegable en **Render** y con una estética **minimalista caricaturesca inspirada en los 80/90**.

## Estado actual del proyecto

El proyecto está en estado funcional y listo para ejecutarse localmente o desplegarse en Render. Actualmente incluye:

- Gameplay completo del ahorcado con selección aleatoria de palabras y pistas.
- Dificultades **Normal** y **Difícil**:
  - Normal: palabras variadas y 1 ayuda.
  - Difícil: palabras de 8 o más caracteres y 2 ayudas.
- Sistema de ayudas para revelar letras pendientes.
- Teclado visual con soporte para alfabeto español, incluyendo `ñ`.
- Normalización de vocales acentuadas para mejorar la jugabilidad (`á`, `é`, `í`, `ó`, `ú`).
- Contador de errores, vidas restantes y porcentaje de progreso de la palabra.
- Estados de partida: jugando, victoria y derrota.
- Escenarios visuales aleatorios y figura del ahorcado progresiva hasta 8 errores.
- Modal de nueva partida y barras laterales desplegables para resumen de la partida.
- Sesión de juego basada en `signed_cookies`, por lo que no depende de guardar partidas en base de datos.
- Endpoint de health check en `/health/`.
- Tests de lógica y vistas con `django.test.TestCase`.

## Stack tecnológico

- **Python 3.13**
- **Django 5.2.12**
- **Gunicorn 23.0.0** como servidor WSGI en producción.
- **WhiteNoise 6.9.0** para servir archivos estáticos comprimidos.
- **dj-database-url 3.0.1** para parsear `DATABASE_URL`.
- **PostgreSQL** en Render para producción.
- **SQLite** como fallback local cuando no existe `DATABASE_URL`.
- **HTML, CSS y JavaScript vanilla** para la interfaz.
- **Render** como plataforma de despliegue.

## Lo que ya viene resuelto

- Configuración productiva para Render.
- `gunicorn` listo en `requirements.txt`.
- `WhiteNoise` configurado con `CompressedManifestStaticFilesStorage`.
- `DATABASE_URL` para PostgreSQL mediante `dj-database-url`.
- `render.yaml` para crear el servicio web y la base en Render.
- `healthCheckPath` en `/health/`.
- `build.sh` para instalar dependencias, correr `collectstatic` y ejecutar migraciones.
- Fallback local con SQLite para probar sin PostgreSQL.
- `ALLOWED_HOSTS` y `CSRF_TRUSTED_ORIGINS` configurables por variables de entorno.
- Compatibilidad automática con `RENDER_EXTERNAL_HOSTNAME`.

## Comandos de Render

### Build Command

```bash
./build.sh
```

### Start Command

```bash
gunicorn ahorcado.wsgi:application
```

> Importante: **Gunicorn debe estar en `requirements.txt`**. Si no está instalado, Render falla al iniciar con `command not found`.

## Variables de entorno para el despliegue

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

- una base PostgreSQL llamada `ahorcado-db`;
- un web service llamado `ahorcado-django`;
- `buildCommand`;
- `startCommand`;
- variables de entorno;
- `healthCheckPath`.

Con eso se evita configurar manualmente los puntos críticos del despliegue.

## Deploy manual en Render

1. Crear un **PostgreSQL** en Render.
2. Crear un **Web Service** desde el repo.
3. Usar:
   - **Build Command:** `./build.sh`
   - **Start Command:** `gunicorn ahorcado.wsgi:application`
4. Cargar las variables de entorno.
5. Pegar el `connectionString` del Postgres en `DATABASE_URL`.

## Correr localmente

```bash
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
# o .venv\Scripts\activate en Windows
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

Luego abrir:

```text
http://127.0.0.1:8000/
```

## Ejecutar tests

```bash
python manage.py test
```

## Health check

- Endpoint: `/health/`
- Respuesta esperada: `ok`
- Content-Type: `text/plain`

## Notas importantes

- En producción, los archivos estáticos los sirve **WhiteNoise**.
- El proyecto usa `signed_cookies` para la sesión del juego, así que el gameplay no depende del motor de sesión en base de datos.
- Igual se ejecutan migraciones porque Django sigue necesitando consistencia para admin, auth y posibles extensiones futuras.
- `DEBUG` viene desactivado por defecto salvo que se configure explícitamente como `true`, `1`, `yes` u `on`.

## Estructura

```text
ahorcado_render_project/
├── ahorcado/                 # Configuración Django del proyecto
├── app/                      # App principal del juego
│   ├── static/app/css/       # Estilos
│   ├── static/app/js/        # JavaScript vanilla
│   ├── templates/app/        # Templates HTML
│   ├── tests.py              # Tests de lógica y vistas
│   ├── views.py              # Vistas y lógica de partida
│   └── words.py              # Banco de palabras y pistas
├── images/                   # Recursos estáticos globales
├── build.sh                  # Script de build para Render
├── manage.py
├── render.yaml               # Infraestructura declarativa para Render
├── requirements.txt
└── README.md
```

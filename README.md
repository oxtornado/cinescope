# CineScope - Clon de Letterboxd

CineScope es una aplicación web para reseñar y descubrir películas, inspirada en Letterboxd.

## Requisitos Previos

- Docker
- Docker Compose
- Una cuenta de API en TMDB (The Movie Database)

## Configuración Inicial

1. Clona el repositorio:
```bash
git clone <url-del-repositorio>
cd letterboxd_clone
```

2. Copia el archivo de variables de entorno:
```bash
cp .env.example .env
```

3. Edita el archivo .env con tus configuraciones:
- Añade tu API key de TMDB
- Modifica las credenciales de la base de datos si es necesario
- Ajusta otras variables según necesites

## Despliegue con Docker

1. Construye y levanta los contenedores:
```bash
docker-compose up --build -d
```

2. Crea un superusuario (la primera vez):
```bash
docker-compose exec web python manage.py createsuperuser
```

3. La aplicación estará disponible en:
- Web: http://localhost:80
- Admin: http://localhost:80/admin

## Estructura del Proyecto

- `movies/`: Aplicación principal de Django
- `root/`: Configuración del proyecto Django
- `nginx/`: Configuración del servidor web
- `static/`: Archivos estáticos
- `mediafiles/`: Archivos subidos por usuarios
- `docker-compose.yml`: Configuración de servicios Docker
- `Dockerfile`: Instrucciones de construcción de la imagen
- `requirements.txt`: Dependencias de Python

## Características

- Sistema de autenticación de usuarios
- Búsqueda de películas usando la API de TMDB
- Sistema de reseñas y calificaciones
- Watchlist personal
- Perfiles de usuario personalizables
- Interfaz responsive con tema oscuro

## Desarrollo

Para desarrollo local sin Docker:

1. Crea un entorno virtual:
```bash
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# o
.venv\Scripts\activate  # Windows
```

2. Instala las dependencias:
```bash
pip install -r requirements.txt
```

3. Configura la base de datos PostgreSQL local

4. Ejecuta las migraciones:
```bash
python manage.py migrate
```

5. Inicia el servidor de desarrollo:
```bash
python manage.py runserver
```

## Mantenimiento

- **Logs**: Los logs están disponibles mediante Docker Compose:
```bash
docker-compose logs -f
```

- **Backups**: Para respaldar la base de datos:
```bash
docker-compose exec db pg_dump -U oxtornado cinescope_db > backup.sql
```

- **Restauración**: Para restaurar un backup:
```bash
docker-compose exec -T db psql -U oxtornado cinescope_db < backup.sql
```

## Seguridad

- Las variables sensibles están en .env (no incluido en el repositorio)
- HTTPS configurado en producción
- Protección contra CSRF habilitada
- Contraseñas hasheadas
- Rate limiting en endpoints sensibles

## Contribución

1. Haz fork del repositorio
2. Crea una rama para tu feature
3. Haz commit de tus cambios
4. Envía un pull request

## Licencia

Este proyecto está bajo la licencia MIT.
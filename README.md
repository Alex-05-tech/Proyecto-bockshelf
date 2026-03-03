================================================================================
  📚 BOOKSHELF — README
================================================================================

Aplicación web para gestionar y descubrir libros, construida con Flask,
MySQL y Docker. Permite explorar un catálogo de libros, registrar lecturas,
dejar valoraciones y comentarios.


================================================================================
  🐳 ARQUITECTURA DOCKER — CONEXIÓN ENTRE CONTENEDORES
================================================================================

  ┌─────────────────┐        ┌─────────────────┐        ┌─────────────────┐
  │                 │        │                 │        │                 │
  │   FRONTEND      │──────▶│    BACKEND      │──────▶│   BASE DATOS    │
  │                 │        │                 │        │                 │
  │ bookshelf_      │        │ bookshelf_      │        │ bookshelf_db    │
  │ frontend        │        │ backend         │        │                 │
  │                 │        │                 │        │                 │
  │ Flask           │        │ Flask API REST  │        │ MySQL 8.0       │
  │ Jinja2          │        │                 │        │                 │
  │ Puerto: 8000    │        │ Puerto: 5000    │        │ Puerto: 3306    │
  │                 │        │                 │        │ (→ 3307 local)  │
  └────────┬────────┘        └────────┬────────┘        └────────┬────────┘
           │                          │                          │
     localhost:8000            http://backend:5000          db:3306
     (navegador)               (red interna Docker)    (red interna Docker)

  ┌─────────────────────────────────────────────────────────────────────────┐
  │                        PUERTOS EXPUESTOS                                │
  │  localhost:8000  ──▶  Frontend   (acceso desde el navegador)           │
  │  localhost:5000  ──▶  Backend    (API REST, acceso opcional)            │
  │  localhost:3307  ──▶  MySQL      (acceso externo / depuración)          │
  └─────────────────────────────────────────────────────────────────────────┘

  ┌─────────────────────────────────────────────────────────────────────────┐
  │                   ORDEN DE ARRANQUE (depends_on)                        │
  │                                                                         │
  │   1. bookshelf_db        ◀── arranca primero                           │
  │            │                 healthcheck: mysqladmin ping               │
  │            ▼                                                            │
  │   2. bookshelf_backend   ◀── espera a que la DB esté lista             │
  │            │                 healthcheck: GET /api/health               │
  │            ▼                                                            │
  │   3. bookshelf_frontend  ◀── espera a que el backend esté listo        │
  └─────────────────────────────────────────────────────────────────────────┘


================================================================================
  🗂  ESTRUCTURA DEL PROYECTO
================================================================================

  bookshelf/
  ├── docker-compose.yml
  ├── backend/
  │   ├── app.py                  API REST (Flask)
  │   ├── requirements.txt
  │   ├── Dockerfile
  │   └── bookshelf.sql           Esquema y datos iniciales de la BD
  └── frontend/
      ├── app.py                  Servidor web (Flask + Jinja2)
      ├── requirements.txt
      ├── Dockerfile
      └── templates/
          ├── base.html
          ├── index.html
          ├── book_detail.html
          ├── book_form.html
          ├── my_books.html
          ├── admin.html
          ├── login.html
          └── register.html


================================================================================
  ⚙️  TECNOLOGÍAS UTILIZADAS
================================================================================

  · Backend:          Python 3 + Flask + mysql-connector-python
  · Frontend:         Python 3 + Flask (plantillas Jinja2)
  · Base de datos:    MySQL 8.0
  · Contenerización:  Docker + Docker Compose
  · Servidor WSGI:    Gunicorn


================================================================================
  🚀 INSTALACIÓN Y PUESTA EN MARCHA
================================================================================

  REQUISITOS PREVIOS
  · Docker Desktop instalado y en ejecución  (https://www.docker.com)
  · Git

  PASOS

  1. Clona el repositorio
       git clone https://github.com/tu-usuario/tu-repositorio.git
       cd tu-repositorio

  2. Verifica que bookshelf.sql esté dentro de la carpeta backend/

  3. Levanta los contenedores
       docker compose up --build

  4. Accede a la aplicación
       · Frontend:    http://localhost:8000
       · Backend API: http://localhost:5000
       · MySQL:       localhost:3307

  5. Para detener
       docker compose down

     Para detener y BORRAR datos:
       docker compose down -v


================================================================================
  🔑 CREDENCIALES POR DEFECTO
================================================================================

  Rol      Usuario    Contraseña
  -------  ---------  ----------
  Admin    admin      admin123

  ⚠ Cambia estas credenciales antes de desplegar en producción.


================================================================================
  ✨ FUNCIONALIDADES
================================================================================

  USUARIO GENERAL
  · Explorar catálogo con búsqueda por título/autor y filtro por género
  · Registrar estado de lectura: Quiero leer · Leyendo · Leído
  · Valorar libros del 1 al 5 estrellas
  · Dejar comentarios personales
  · Ver resumen en "Mis Libros"

  ADMINISTRADOR
  · Panel para gestionar el catálogo completo
  · Añadir, editar y eliminar libros
  · Portada mediante URL o color de fondo personalizado
  · Vista previa de portada en tiempo real


================================================================================
  🔌 API REST — ENDPOINTS DEL BACKEND
================================================================================

  Método    Endpoint                          Descripción
  --------  --------------------------------  --------------------------------
  GET       /api/health                       Estado del servidor
  POST      /api/login                        Iniciar sesión
  POST      /api/register                     Registrar usuario
  GET       /api/books                        Listar libros (?q= y ?genre=)
  GET       /api/books/:id                    Detalle de un libro
  POST      /api/books                        Añadir libro
  PUT       /api/books/:id                    Editar libro
  DELETE    /api/books/:id                    Eliminar libro
  GET       /api/user/:uid/books              Libros del usuario
  GET       /api/user/:uid/books/:bid         Estado de un libro
  POST      /api/user/:uid/books/:bid         Actualizar estado / valoración


================================================================================
  🗄️  BASE DE DATOS
================================================================================

  Inicializada automáticamente con backend/bookshelf.sql:

  · users       Usuarios registrados
  · books       Catálogo de libros
  · user_books  Relación usuario-libro (estado, valoración, comentario)

  Incluye admin por defecto y 15 libros de ejemplo:
  Mistborn, El Archivo de las Tormentas, El Nombre del Viento,
  La Sombra del Viento, Cien Años de Soledad, 1984, Fundación...


================================================================================
  🐳 VARIABLES DE ENTORNO
================================================================================

  BACKEND
  DB_HOST        db                     Host de MySQL
  DB_USER        bookshelf_user         Usuario de MySQL
  DB_PASSWORD    bookshelf_pass         Contraseña de MySQL
  DB_NAME        bookshelf              Nombre de la base de datos

  FRONTEND
  API_URL        http://backend:5000    URL del backend
  SECRET_KEY     bookshelf_docker_secret_2024   Clave secreta Flask

================================================================================

================================================================================
  🧪 PRUEBAS CON POSTMAN
================================================================================

  Se incluye una colección de pruebas Postman en:
  docs/Bookshelf_Tests_Postman.json

  Para usarla:
  1. Abre Postman
  2. Importar → selecciona el archivo JSON
  3. Asegúrate de tener los contenedores levantados (docker compose up --build)
  4. Ejecuta las peticiones contra http://localhost:5000

================================================================================

prueba de action
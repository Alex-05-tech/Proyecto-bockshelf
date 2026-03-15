# 📚 Bookshelf

Aplicación web para gestionar y descubrir libros, construida con Flask, MySQL y Docker.

---

## 🐳 Arquitectura Docker

```
┌─────────────────┐        ┌─────────────────┐        ┌─────────────────┐
│   FRONTEND      │──────▶ │    BACKEND      │──────▶ │   BASE DATOS    │
│                 │        │                 │        │                 │
│ Flask · Jinja2  │        │ Flask API REST  │        │ MySQL 8.0       │
│ Puerto: 8000    │        │ Puerto: 5000    │        │ Puerto: 3306    │
└─────────────────┘        └─────────────────┘        └─────────────────┘
localhost:8000             http://backend:5000         db:3306
(navegador)                (red interna Docker)        (red interna Docker)
```
<img width="1608" height="172" alt="image" src="https://github.com/user-attachments/assets/d094fb34-c092-4bd9-87b1-a195f9ae112c" />

---

## 🗂 Estructura del proyecto

```
bookshelf_v3/
├── docker-compose.yml
├── .github/workflows/ci-cd.yml
├── backend/
│   ├── app.py
│   ├── requirements.txt
│   ├── Dockerfile
│   └── bookshelf.sql
├── frontend/
│   ├── app.py
│   ├── requirements.txt
│   ├── Dockerfile
│   └── templates/
└── tests/
    ├── backend/
    └── frontend/
```

---

## 🚀 Instalación

**Requisitos:** Docker Desktop y Git

```bash
# 1. Clona el repositorio
git clone https://github.com/tu-usuario/tu-repositorio.git
cd tu-repositorio

# 2. Levanta los contenedores
docker compose up --build

# 3. Accede en el navegador
http://localhost:8000

# 4. Para detener
docker compose down
```

---

## 🔑 Credenciales por defecto

| Rol   | Usuario | Contraseña |
|-------|---------|------------|
| Admin | admin   | admin123   |

> ⚠️ Cambiar antes de desplegar en producción.

---

## ✨ Funcionalidades

- Explorar catálogo de libros con búsqueda y filtro por género
- Registrar estado de lectura: Quiero leer · Leyendo · Leído
- Valorar libros y dejar comentarios
- Panel de administración para gestionar el catálogo

Imagen de la Web en funcionamiento
<img width="941" height="491" alt="Captura de pantalla 2026-03-04 192450" src="https://github.com/user-attachments/assets/7da80d45-033f-42ac-85d2-fdce0c0a39ec" />


---

## 🔄 CI/CD — GitHub Actions

Pipeline automático en cada push o pull request a `main`/`master`.

🧪 Job 1 — Tests Backend

    * Levanta un contenedor MySQL 8.0 con las mismas credenciales que producción
    * Inicializa la base de datos con bookshelf.sql
    * Arranca el backend y comprueba que /api/health responde correctamente

🧪 Job 2 — Tests Frontend

    * Instala las dependencias del frontend
    * Compila app.py para verificar que no hay errores de sintaxis

🐳 Job 3 — Build Docker (solo si los dos anteriores pasan)

    * Levanta los 3 contenedores con docker compose up
    * Verifica que el backend responde en http://localhost:5000/api/health
    * Verifica que el frontend responde en http://localhost:8000
    * Limpia los contenedores al finalizar

  
<img width="632" height="187" alt="Captura de pantalla 2026-03-09 173333" src="https://github.com/user-attachments/assets/370f572e-c308-4cfd-bffa-0a33f663fda4" />

---

## 🧪 Pruebas

Se incluye también una colección Postman en `docs/Bookshelf_Tests_Postman.json` (Hay mas pruebas realizadas)
<img width="1064" height="276" alt="Captura de pantalla 2026-03-04 192655" src="https://github.com/user-attachments/assets/a1160155-90c4-45d5-9c56-5fc03fb3a888" />


Pruebas con Pytest organizadas en `tests/backend/` y `tests/frontend/`.


Backend — `tests/backend/`

| Archivo            | Tipo          | Qué prueba                                        |
|--------------------|---------------|---------------------------------------------------|
| test_health.py     | Unitaria      | El servidor responde correctamente en /api/health |
| test_auth.py       | Integración   | Registro de usuario, login correcto y fallido     |
| test_book.py       | Integración   | Listar, buscar, añadir, editar y borrar libros    |
| test_user_books.py | Integración   | Valoraciones, comentarios y estados de lectura    |

Imagen de comprobación:
<img width="1365" height="388" alt="Captura de pantalla 2026-03-04 192232" src="https://github.com/user-attachments/assets/ae5bca5f-cbb6-4ff1-9739-83025b4268b5" />


Fronrtend — `tests/frontend/`

| Archivo            | Tipo          | Qué prueba                                        |
|--------------------|---------------|---------------------------------------------------|
| test_sintaxish.py  | Unitaria      | Sintaxis correcta e imports necesarios en app.py  |
| test_rutas.py      | Integración   | Las rutas cargan y redirigen correctamente        |

Imagen de comprobación:
<img width="1375" height="245" alt="Captura de pantalla 2026-03-04 192317" src="https://github.com/user-attachments/assets/6f4d0087-ca21-49f0-befc-ba8bc3ac3ed4" />

<<<<<<< HEAD
### Pruebas de seguridad OWASP — `tests/backend/test_seguridad.py`

Pruebas que verifican que las medidas OWASP implementadas funcionan correctamente:

| Prueba                              | OWASP | Qué verifica                                        |
|-------------------------------------|-------|-----------------------------------------------------|
| test_acceso_admin_sin_sesion        | A01   | Borrar libros sin autenticación devuelve 401/403    |
| test_acceso_libros_usuario_ajeno    | A01   | Acceder a datos de otro usuario devuelve 401/403    |
| test_inyeccion_sql_login            | A03   | Payloads de inyección SQL son rechazados            |
| test_inyeccion_sql_busqueda         | A03   | Búsquedas maliciosas no causan error 500            |
| test_rate_limiting_login            | A04   | Tras 5 intentos fallidos devuelve 429               |
| test_login_campos_vacios            | A07   | Login con campos vacíos es rechazado                |
| test_login_credenciales_incorrectas | A07   | Credenciales incorrectas devuelven 401              |
| test_mensaje_error_generico         | A07   | El error no revela si el usuario existe o no        |
| test_cabeceras_seguridad            | A05   | Cabeceras HTTP de seguridad presentes               |
| test_registro_campos_largos         | A03   | Campos demasiado largos son rechazados              |
| test_registro_email_invalido        | A03   | Email con formato inválido es rechazado             |

![alt text](image.png)
=======


```bash
cd bookshelf_v3/backend
pytest tests/ -v
```

---

## 🔐 Seguridad — OWASP Top 10

| #   | Vulnerabilidad          | Medida aplicada                                  |
|-----|-------------------------|--------------------------------------------------|
| A01 | Control de acceso       | Rutas protegidas con login y rol de admin        |
| A02 | Criptografía            | Contraseñas con hash SHA-256 y salt              |
| A03 | Inyección               | Consultas SQL parametrizadas                     |
| A04 | Diseño inseguro         | Rate limiting en login (5 intentos / 5 min)      |
| A05 | Configuración           | Cabeceras HTTP de seguridad y debug=False        |
| A06 | Componentes             | Versiones fijadas en requirements.txt            |
| A07 | Autenticación           | Sesiones Flask y mensajes de error genéricos     |
| A08 | Integridad              | Pipeline CI/CD que verifica cada commit          |
| A09 | Logging                 | Registro de eventos de seguridad                 |

## 🔐 Seguridad — OWASP Top 10 API Security

| # | Vulnerabilidad | Medida Aplicada |
|:-:|:---|:---|
| `API1` | **Broken Object Level Authorization**      | Cada endpoint valida que el usuario accede solo a sus propios datos |
| `API2` | **Broken Authentication**                  | Sesiones Flask con `SECRET_KEY` y expiración de sesión configurada |
| `API3` | **Broken Object Property Level Auth**      | La API devuelve únicamente los campos necesarios en cada respuesta |
| `API4` | **Unrestricted Resource Consumption**      | Rate limiting en login — máximo 5 intentos cada 5 minutos |
| `API5` | **Broken Function Level Authorization**    | Endpoints de admin protegidos con el decorador `@admin_required` |
| `API6` | **Unrestricted Access to Sensitive Flows** | Registro y login con validación estricta y límites de acceso |
| `API7` | **Server Side Request Forgery**            | Riesgo bajo — no se realizan peticiones a URLs externas |
| `API8` | **Security Misconfiguration**              | Cabeceras HTTP de seguridad aplicadas en todas las respuestas |
| `API9` | **Improper Inventory Management**          | Entorno único y controlado mediante Docker y CI/CD |
| `API10` | **Unsafe Consumption of APIs**            | El frontend valida y sanitiza todas las respuestas del backend |

## 🔐 Dónde está implementado OWASP en el código

### `bookshelf_v3/backend/app.py`

| OWASP | Función / Sección | Qué hace |
|-------|-------------------|----------|
| A01   | `def require_auth(f)`                | Bloquea endpoints sin cabecera `X-User-Id` |
| A02   | `def hash_pw(pw)`                    | SHA-256 + salt desde variable de entorno |
| A03   | `def validate_username / validate_email / validate_password` | Valida formato y longitud de inputs |
| A03   | Todas las queries SQL                | Usan `%s` con parámetros, nunca concatenación directa |
| A04   | `def check_rate_limit(ip)`           | Máximo 5 intentos por IP en 5 minutos |
| A05   | `def add_security_headers(response)` | Añade `X-Frame-Options`, `X-XSS-Protection`, etc. |
| A07   | `def login()` → mensaje de error     | Siempre devuelve `"Usuario o contraseña incorrectos"` |
| A09   | `logger.warning / logger.info`       | Registra logins correctos, fallidos y rate limit |

### `bookshelf_v3/frontend/app.py`

| OWASP | Función / Sección | Qué hace |
|-------|-------------------|----------|
| A01   | `def login_required(f)` | Protege rutas que requieren sesión activa |
| A01   | `def admin_required(f)` | Protege rutas exclusivas de administrador |
| A01   | `def auth_headers()`    | Envía `X-User-Id` al backend en cada petición |

### `bookshelf_v3/backend/bookshelf.sql`

| OWASP | Sección | Qué hace |
|-------|---------|----------|
| A02   | Hash del usuario admin | Contraseña almacenada como SHA-256 + salt, nunca en texto plano |

### `docker-compose.yml`

| OWASP | Sección | Qué hace |
|-------|---------|----------|
| A05   | `environment` de cada servicio          | `SECRET_KEY` y credenciales fuera del código fuente |
| A08   | Junto con `.github/workflows/ci-cd.yml` | Pipeline que verifica cada commit antes de desplegar |

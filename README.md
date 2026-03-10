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
<img width="941" height="491" alt="image" src="https://github.com/user-attachments/assets/8d7dd511-1dde-4255-a4e4-2d91a7e59b29" />


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

  
<img width="632" height="187" alt="Captura de pantalla 2026-03-09 173333" src="https://github.com/user-attachments/assets/157abdd7-658a-4a2b-b5dd-a67490228259" />

---

## 🧪 Pruebas

Se incluye también una colección Postman en `docs/Bookshelf_Tests_Postman.json` (Hay mas pruebas realizadas)
<img width="1064" height="276" alt="image" src="https://github.com/user-attachments/assets/3e0b9aa2-95ff-4aeb-8740-d51853949c4b" />


Pruebas con Pytest organizadas en `tests/backend/` y `tests/frontend/`.


Backend — `tests/backend/`

| Archivo            | Tipo          | Qué prueba                                        |
|--------------------|---------------|---------------------------------------------------|
| test_health.py     | Unitaria      | El servidor responde correctamente en /api/health |
| test_auth.py       | Integración   | Registro de usuario, login correcto y fallido     |
| test_book.py       | Integración   | Listar, buscar, añadir, editar y borrar libros    |
| test_user_books.py | Integración   | Valoraciones, comentarios y estados de lectura    |

Imagen de comprobación:
<img width="1365" height="388" alt="image" src="https://github.com/user-attachments/assets/f63251a9-ae4e-4e85-9c8a-ce4141840da0" />


Fronrtend — `tests/frontend/`

| Archivo            | Tipo          | Qué prueba                                        |
|--------------------|---------------|---------------------------------------------------|
| test_sintaxish.py  | Unitaria      | Sintaxis correcta e imports necesarios en app.py  |
| test_rutas.py      | Integración   | Las rutas cargan y redirigen correctamente        |

Imagen de comprobación:
<img width="1375" height="245" alt="image" src="https://github.com/user-attachments/assets/7c2f0405-9179-4ec1-ac1d-c6d31e5721f9" />



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

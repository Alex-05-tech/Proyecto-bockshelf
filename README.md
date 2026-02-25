# 📚 Bookshelf

## 📁 Estructura del proyecto

```
bookshelf/
│
├── backend/                  ← Todo el servidor Python
│   ├── app.py                ← Aplicación Flask + rutas + lógica
│   ├── requirements.txt      ← Dependencias Python
│   └── bookshelf.sql         ← Base de datos MySQL (importar en phpMyAdmin)
│
└── frontend/                 ← Todo lo visual
    ├── templates/            ← Plantillas HTML (Jinja2)
    │   ├── base.html         ← Plantilla base (nav, estilos)
    │   ├── index.html        ← Catálogo de libros
    │   ├── book_detail.html  ← Ficha de libro
    │   ├── my_books.html     ← Biblioteca personal
    │   ├── admin.html        ← Panel de administración
    │   ├── book_form.html    ← Formulario añadir/editar
    │   ├── login.html        ← Inicio de sesión
    │   └── register.html     ← Registro
    └── static/               ← Archivos estáticos (CSS, JS, imágenes)
        ├── css/
        └── js/
```

---

## ⚙️ Puesta en marcha

### 1. Importar la base de datos
- Abre **phpMyAdmin** → **Importar**
- Selecciona `backend/bookshelf.sql` → **Continuar**

### 2. Configurar conexión MySQL
Edita `backend/app.py` línea ~20:
```python
DB_CONFIG = {
    'host':     'localhost',
    'user':     'root',
    'password': '',   # ← tu contraseña aquí
    'database': 'bookshelf',
}
```

### 3. Instalar dependencias
```bash
cd backend
pip install -r requirements.txt
```

### 4. Arrancar el servidor
```bash
cd backend
python app.py
```

Abre el navegador en **http://localhost:8000**

---

## 🔑 Credenciales por defecto
| Usuario | Contraseña | Rol |
|---------|-----------|-----|
| admin   | admin123  | Administrador |

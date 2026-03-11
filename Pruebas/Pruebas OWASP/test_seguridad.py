"""
test_seguridad.py — Pruebas de seguridad OWASP
Verifican que las medidas de seguridad implementadas funcionan correctamente.
<<<<<<< HEAD
Ejecutar con los contenedores levantados: python -m pytest test_seguridad.py -v
=======
Ejecutar con los contenedores levantados: pytest tests/backend/test_seguridad.py -v
>>>>>>> 1e7743d2380a19f8f9754ed10483e1dadc537efb
"""

import requests

BASE = "http://localhost:5000/api"


# ── A01 · Control de acceso ───────────────────────────────────────────────────

def test_acceso_admin_sin_sesion():
<<<<<<< HEAD
    """Un usuario sin sesión no puede borrar libros."""
=======
    """Un usuario sin sesión no puede acceder a endpoints de admin."""
>>>>>>> 1e7743d2380a19f8f9754ed10483e1dadc537efb
    r = requests.delete(f"{BASE}/books/1")
    assert r.status_code in [401, 403], "Debe bloquear el borrado sin autenticación"

def test_acceso_libros_usuario_ajeno():
<<<<<<< HEAD
    """Sin autenticación no se puede acceder a los libros de un usuario."""
    r = requests.get(f"{BASE}/user/9999/books")
    assert r.status_code in [401, 403], "No debe permitir acceder a datos sin autenticación"
=======
    """Un usuario no puede ver los libros de otro usuario."""
    r = requests.get(f"{BASE}/user/9999/books")
    assert r.status_code in [401, 403], "No debe permitir acceder a datos de otro usuario"
>>>>>>> 1e7743d2380a19f8f9754ed10483e1dadc537efb


# ── A03 · Inyección SQL ───────────────────────────────────────────────────────

def test_inyeccion_sql_login():
<<<<<<< HEAD
    """Un intento de inyección SQL en el login debe ser rechazado (400 o 401)."""
    payloads = [
        {"username": "' OR '1'='1", "password": "cualquiera"},
        {"username": "admin'--",    "password": "cualquiera"},
        {"username": "' OR 1=1--", "password": "x"},
    ]
    for payload in payloads:
        r = requests.post(f"{BASE}/login", json=payload)
        assert r.status_code in [400, 401], \
            f"Inyección SQL no bloqueada: {payload['username']} → {r.status_code}"
=======
    """Un intento de inyección SQL en el login debe ser rechazado."""
    payloads = [
        {"username": "' OR '1'='1", "password": "cualquiera"},
        {"username": "admin'--", "password": "cualquiera"},
        {"username": "' OR 1=1--", "password": ""},
    ]
    for payload in payloads:
        r = requests.post(f"{BASE}/login", json=payload)
        assert r.status_code == 401, f"Inyección SQL no bloqueada: {payload['username']}"
>>>>>>> 1e7743d2380a19f8f9754ed10483e1dadc537efb

def test_inyeccion_sql_busqueda():
    """Una búsqueda con inyección SQL no debe provocar error 500."""
    params = [
        "' OR '1'='1",
        "'; DROP TABLE books;--",
        "' UNION SELECT 1,2,3--",
    ]
    for q in params:
        r = requests.get(f"{BASE}/books", params={"q": q})
        assert r.status_code != 500, f"La búsqueda causó error 500 con: {q}"


# ── A04 · Rate Limiting ───────────────────────────────────────────────────────

def test_rate_limiting_login():
    """Después de 5 intentos fallidos debe devolver 429."""
<<<<<<< HEAD
    payload = {"username": "usuarioquenoexiste_ratelimit", "password": "incorrecta"}
=======
    payload = {"username": "admin", "password": "contraseña_incorrecta"}
>>>>>>> 1e7743d2380a19f8f9754ed10483e1dadc537efb
    status_codes = []
    for _ in range(7):
        r = requests.post(f"{BASE}/login", json=payload)
        status_codes.append(r.status_code)
    assert 429 in status_codes, "El rate limiting no está funcionando (esperaba HTTP 429)"


# ── A07 · Autenticación ───────────────────────────────────────────────────────

def test_login_campos_vacios():
<<<<<<< HEAD
    """El login con campos vacíos debe ser rechazado con 400."""
    casos = [
        {"username": "", "password": ""},
        {"username": "usuariovacio", "password": ""},
=======
    """El login con campos vacíos debe ser rechazado."""
    casos = [
        {"username": "", "password": ""},
        {"username": "admin", "password": ""},
>>>>>>> 1e7743d2380a19f8f9754ed10483e1dadc537efb
        {"username": "", "password": "admin123"},
    ]
    for caso in casos:
        r = requests.post(f"{BASE}/login", json=caso)
<<<<<<< HEAD
        assert r.status_code in [400, 401, 429], \
            f"Login con campos vacíos no rechazado: {caso} → {r.status_code}"

def test_login_credenciales_incorrectas():
    """El login con credenciales incorrectas devuelve 401 o 429 (rate limit)."""
    r = requests.post(f"{BASE}/login", json={"username": "admin_test_creds", "password": "incorrecta"})
    assert r.status_code in [401, 429], f"Esperaba 401 o 429, recibió {r.status_code}"

def test_mensaje_error_generico():
    """El mensaje de error no revela si el usuario existe o no."""
    r1 = requests.post(f"{BASE}/login", json={"username": "admin",                   "password": "mal_x1"})
    r2 = requests.post(f"{BASE}/login", json={"username": "usuarioquenoexiste_msg", "password": "mal_x1"})
    if r1.status_code == 401 and r2.status_code == 401:
        assert r1.json().get("error") == r2.json().get("error"), \
            "El mensaje de error revela si el usuario existe o no"


# ── A05 · Cabeceras de seguridad ──────────────────────────────────────────────
=======
        assert r.status_code in [400, 401], f"Login con campos vacíos no rechazado: {caso}"

def test_login_credenciales_incorrectas():
    """El login con credenciales incorrectas devuelve 401."""
    r = requests.post(f"{BASE}/login", json={"username": "admin", "password": "incorrecta"})
    assert r.status_code == 401

def test_mensaje_error_generico():
    """El mensaje de error no revela si el usuario existe o no."""
    r1 = requests.post(f"{BASE}/login", json={"username": "admin", "password": "mal"})
    r2 = requests.post(f"{BASE}/login", json={"username": "usuarioquenoexiste", "password": "mal"})
    datos1 = r1.json()
    datos2 = r2.json()
    assert datos1.get("error") == datos2.get("error"), \
        "El mensaje de error revela si el usuario existe o no"


# ── A05 · Cabeceras de seguridad ─────────────────────────────────────────────
>>>>>>> 1e7743d2380a19f8f9754ed10483e1dadc537efb

def test_cabeceras_seguridad():
    """Las respuestas deben incluir las cabeceras HTTP de seguridad."""
    r = requests.get(f"{BASE}/health")
    cabeceras = r.headers
    assert "X-Content-Type-Options" in cabeceras, "Falta cabecera X-Content-Type-Options"
<<<<<<< HEAD
    assert "X-Frame-Options"        in cabeceras, "Falta cabecera X-Frame-Options"
    assert "X-XSS-Protection"       in cabeceras, "Falta cabecera X-XSS-Protection"
=======
    assert "X-Frame-Options" in cabeceras, "Falta cabecera X-Frame-Options"
    assert "X-XSS-Protection" in cabeceras, "Falta cabecera X-XSS-Protection"
>>>>>>> 1e7743d2380a19f8f9754ed10483e1dadc537efb


# ── A03 · Validación de inputs ────────────────────────────────────────────────

def test_registro_campos_demasiado_largos():
    """El registro con campos excesivamente largos debe ser rechazado."""
    r = requests.post(f"{BASE}/register", json={
        "username": "a" * 500,
<<<<<<< HEAD
        "email":    "test@test.com",
        "password": "1234abcd"
    })
    assert r.status_code in [400, 409, 422], \
        f"No se valida la longitud máxima del username → {r.status_code}"
=======
        "email": "test@test.com",
        "password": "1234abcd"
    })
    assert r.status_code in [400, 422], "No se valida la longitud máxima del username"
>>>>>>> 1e7743d2380a19f8f9754ed10483e1dadc537efb

def test_registro_email_invalido():
    """El registro con un email inválido debe ser rechazado."""
    r = requests.post(f"{BASE}/register", json={
<<<<<<< HEAD
        "username": "usuariotest_email",
        "email":    "esto_no_es_un_email",
        "password": "1234abcd"
    })
    assert r.status_code in [400, 422], \
        f"No se valida el formato del email → {r.status_code}"
=======
        "username": "usuariotest",
        "email": "esto_no_es_un_email",
        "password": "1234abcd"
    })
    assert r.status_code in [400, 422], "No se valida el formato del email"
>>>>>>> 1e7743d2380a19f8f9754ed10483e1dadc537efb

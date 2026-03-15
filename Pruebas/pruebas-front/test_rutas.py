import sys
import os

def find_frontend_dir():
    """Busca la carpeta frontend subiendo por el árbol de directorios."""
    current = os.path.dirname(os.path.abspath(__file__))
    for _ in range(6):
        for candidate in [
            os.path.join(current, "frontend"),
            os.path.join(current, "bookshelf_v3", "frontend"),
        ]:
            if os.path.isdir(candidate) and os.path.exists(os.path.join(candidate, "app.py")):
                return candidate
        current = os.path.dirname(current)
    raise FileNotFoundError("No se encontró la carpeta frontend en ningún directorio padre")

sys.path.insert(0, find_frontend_dir())

from unittest.mock import patch, MagicMock
import app as frontend_app

frontend_app.app.config["TESTING"] = True
frontend_app.app.config["SECRET_KEY"] = "test"

client = frontend_app.app.test_client()

def mock_books_response():
    m = MagicMock()
    m.json.return_value = {"books": [], "genres": []}
    m.status_code = 200
    return m

def test_index_carga():
    with patch("app.req.get", return_value=mock_books_response()):
        r = client.get("/")
        assert r.status_code == 200

def test_login_carga():
    r = client.get("/login")
    assert r.status_code == 200

def test_register_carga():
    r = client.get("/register")
    assert r.status_code == 200

def test_my_books_sin_login_redirige():
    r = client.get("/my-books")
    assert r.status_code == 302

def test_admin_sin_login_redirige():
    r = client.get("/admin")
    assert r.status_code == 302
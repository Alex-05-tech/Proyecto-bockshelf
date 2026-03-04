import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

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
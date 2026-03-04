import requests
import time

BASE = "http://localhost:5000"

# Usuario de prueba único para no colisionar
TS = str(int(time.time()))
USER = f"testuser_{TS}"
EMAIL = f"test_{TS}@test.com"
PASS = "password123"

class TestRegistro:
    def test_registro_ok(self):
        r = requests.post(f"{BASE}/api/register", json={
            "username": USER,
            "email": EMAIL,
            "password": PASS
        })
        assert r.status_code == 201
        assert r.json()["ok"] is True

    def test_registro_duplicado(self):
        # Intentar registrar el mismo usuario dos veces
        requests.post(f"{BASE}/api/register", json={
            "username": USER + "_dup",
            "email": EMAIL + "_dup",
            "password": PASS
        })
        r = requests.post(f"{BASE}/api/register", json={
            "username": USER + "_dup",
            "email": EMAIL + "_dup",
            "password": PASS
        })
        assert r.status_code == 409

class TestLogin:
    def test_login_ok(self):
        r = requests.post(f"{BASE}/api/login", json={
            "username": "admin",
            "password": "admin123"
        })
        assert r.status_code == 200
        assert r.json()["ok"] is True
        assert "user" in r.json()

    def test_login_mal_password(self):
        r = requests.post(f"{BASE}/api/login", json={
            "username": "admin",
            "password": "wrongpassword"
        })
        assert r.status_code == 401
        assert r.json()["ok"] is False

    def test_login_usuario_inexistente(self):
        r = requests.post(f"{BASE}/api/login", json={
            "username": "noexiste",
            "password": "noexiste"
        })
        assert r.status_code == 401
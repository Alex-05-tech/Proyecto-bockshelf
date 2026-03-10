import requests

BASE = "http://localhost:5000"

class TestListarLibros:
    def test_listar_ok(self):
        r = requests.get(f"{BASE}/api/books")
        assert r.status_code == 200
        assert "books" in r.json()
        assert "genres" in r.json()

    def test_buscar_por_titulo(self):
        r = requests.get(f"{BASE}/api/books", params={"q": "Mistborn"})
        assert r.status_code == 200
        books = r.json()["books"]
        assert any("Mistborn" in b["title"] for b in books)

    def test_buscar_sin_resultados(self):
        r = requests.get(f"{BASE}/api/books", params={"q": "zzznoresultados999"})
        assert r.status_code == 200
        assert r.json()["books"] == []

    def test_filtrar_por_genero(self):
        r = requests.get(f"{BASE}/api/books", params={"genre": "Fantasía"})
        assert r.status_code == 200
        books = r.json()["books"]
        assert all(b["genre"] == "Fantasía" for b in books)

class TestDetalleLibro:
    def test_detalle_ok(self):
        r = requests.get(f"{BASE}/api/books/1")
        assert r.status_code == 200
        assert "book" in r.json()
        assert r.json()["book"]["id"] == 1

    def test_detalle_no_existe(self):
        r = requests.get(f"{BASE}/api/books/99999")
        assert r.status_code == 404

class TestCRUDLibros:
    def test_añadir_libro(self):
        r = requests.post(f"{BASE}/api/books", json={
            "title": "Libro Test",
            "author": "Autor Test",
            "synopsis": "Sinopsis de prueba",
            "genre": "Test",
            "year": 2024,
            "cover_color": "#123456",
            "created_by": 1
        })
        assert r.status_code == 201
        assert r.json()["ok"] is True
        assert "id" in r.json()
        return r.json()["id"]

    def test_editar_libro(self):
        # Primero añadimos uno
        r = requests.post(f"{BASE}/api/books", json={
            "title": "Libro Editar",
            "author": "Autor",
            "created_by": 1
        })
        bid = r.json()["id"]

        # Editamos
        r2 = requests.put(f"{BASE}/api/books/{bid}", json={
            "title": "Libro Editado",
            "author": "Autor Editado",
            "synopsis": "",
            "genre": "",
            "year": None,
            "cover_color": "#000000"
        })
        assert r2.status_code == 200
        assert r2.json()["ok"] is True

    def test_borrar_libro(self):
        # Primero añadimos uno
        r = requests.post(f"{BASE}/api/books", json={
            "title": "Libro Borrar",
            "author": "Autor",
            "created_by": 1
        })
        bid = r.json()["id"]

        # Borramos
        r2 = requests.delete(f"{BASE}/api/books/{bid}")
        assert r2.status_code == 200
        assert r2.json()["ok"] is True

        # Comprobamos que ya no existe
        r3 = requests.get(f"{BASE}/api/books/{bid}")
        assert r3.status_code == 404
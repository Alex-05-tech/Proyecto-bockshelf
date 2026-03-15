import ast
import os

def find_frontend_app():
    """Busca app.py del frontend subiendo por el árbol de directorios."""
    current = os.path.dirname(os.path.abspath(__file__))
    for _ in range(6):
        for candidate in [
            os.path.join(current, "frontend", "app.py"),
            os.path.join(current, "bookshelf_v3", "frontend", "app.py"),
        ]:
            if os.path.exists(candidate):
                return candidate
        current = os.path.dirname(current)
    raise FileNotFoundError("No se encontró frontend/app.py en ningún directorio padre")

RUTA_APP = find_frontend_app()

def test_sintaxis_app():
    with open(RUTA_APP, "r", encoding="utf-8") as f:
        codigo = f.read()
    try:
        ast.parse(codigo)
    except SyntaxError as e:
        assert False, f"Error de sintaxis en app.py: {e}"

def test_imports_presentes():
    with open(RUTA_APP, "r", encoding="utf-8") as f:
        codigo = f.read()
    assert "from flask import" in codigo
    assert "render_template" in codigo
    assert "session" in codigo
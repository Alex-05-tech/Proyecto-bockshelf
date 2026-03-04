import ast
import os

RUTA_APP = r"C:\Users\ALV\Downloads\Proyecto-PPS-bockshelf-\bookshelf_v3\frontend\app.py"

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
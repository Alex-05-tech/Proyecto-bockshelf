from flask import Flask, render_template, request, redirect, url_for, session, flash
import requests as req
import os

app = Flask(__name__,
            template_folder='templates',
            static_folder='static')

app.secret_key = os.environ.get('SECRET_KEY', 'bookshelf_secret_2024')

# URL del backend (en Docker viene de variable de entorno, en local apunta a localhost)
API = os.environ.get('API_URL', 'http://localhost:5000')

# ── Decoradores ───────────────────────────────────────────────────────────────
from functools import wraps

def login_required(f):
    @wraps(f)
    def wrapped(*args, **kwargs):
        if 'user_id' not in session:
            flash('Debes iniciar sesión primero.', 'info')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return wrapped

def admin_required(f):
    @wraps(f)
    def wrapped(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        if not session.get('is_admin'):
            flash('Acceso restringido a administradores.', 'error')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return wrapped

# ── Rutas principales ─────────────────────────────────────────────────────────
@app.route('/')
def index():
    search = request.args.get('q', '')
    genre  = request.args.get('genre', '')
    params = {}
    if search: params['q']     = search
    if genre:  params['genre'] = genre

    r = req.get(f'{API}/api/books', params=params)
    data   = r.json()
    books  = data.get('books', [])
    genres = data.get('genres', [])

    # Estado de cada libro para el usuario logueado
    user_books = {}
    if 'user_id' in session:
        r2 = req.get(f'{API}/api/user/{session["user_id"]}/books')
        for b in r2.json().get('books', []):
            user_books[b['id']] = b

    return render_template('index.html', books=books, genres=genres,
                           user_books=user_books, search=search, current_genre=genre)

@app.route('/book/<int:bid>')
def book_detail(bid):
    r = req.get(f'{API}/api/books/{bid}')
    if r.status_code == 404:
        flash('Libro no encontrado.', 'error')
        return redirect(url_for('index'))
    data    = r.json()
    book    = data['book']
    reviews = data['reviews']
    stats   = data['stats']

    user_book = None
    if 'user_id' in session:
        r2 = req.get(f'{API}/api/user/{session["user_id"]}/books/{bid}')
        user_book = r2.json().get('user_book')

    return render_template('book_detail.html', book=book, reviews=reviews,
                           user_book=user_book, stats=stats)

@app.route('/book/<int:bid>/update', methods=['POST'])
@login_required
def update_user_book(bid):
    liked_v = request.form.get('liked', '')
    payload = {
        'status':  request.form.get('status', 'quiero_leer'),
        'rating':  request.form.get('rating') or None,
        'liked':   int(liked_v) if liked_v != '' else None,
        'comment': request.form.get('comment', '').strip()
    }
    req.post(f'{API}/api/user/{session["user_id"]}/books/{bid}', json=payload)
    flash('¡Tu lectura ha sido actualizada!', 'success')
    return redirect(url_for('book_detail', bid=bid))

@app.route('/my-books')
@login_required
def my_books():
    r = req.get(f'{API}/api/user/{session["user_id"]}/books')
    all_books = r.json().get('books', [])
    reading = [b for b in all_books if b['status'] == 'leyendo']
    read    = [b for b in all_books if b['status'] == 'leido']
    want    = [b for b in all_books if b['status'] == 'quiero_leer']
    return render_template('my_books.html', reading=reading, read=read, want=want)

# ── Admin ─────────────────────────────────────────────────────────────────────
@app.route('/admin')
@admin_required
def admin():
    books = req.get(f'{API}/api/books').json().get('books', [])
    return render_template('admin.html', books=books, users=[])

@app.route('/admin/book/add', methods=['GET', 'POST'])
@admin_required
def add_book():
    if request.method == 'POST':
        payload = {
            'title':       request.form['title'],
            'author':      request.form['author'],
            'synopsis':    request.form.get('synopsis',''),
            'genre':       request.form.get('genre',''),
            'year':        request.form.get('year') or None,
            'cover_color': request.form.get('cover_color','#7c6f64'),
            'cover_image': request.form.get('cover_image','').strip() or None,
            'created_by':  session['user_id']
        }
        req.post(f'{API}/api/books', json=payload)
        flash('Libro añadido correctamente.', 'success')
        return redirect(url_for('admin'))
    return render_template('book_form.html', book=None, action='Añadir')

@app.route('/admin/book/edit/<int:bid>', methods=['GET', 'POST'])
@admin_required
def edit_book(bid):
    r    = req.get(f'{API}/api/books/{bid}')
    book = r.json().get('book')
    if not book:
        flash('Libro no encontrado.', 'error')
        return redirect(url_for('admin'))
    if request.method == 'POST':
        payload = {
            'title':       request.form['title'],
            'author':      request.form['author'],
            'synopsis':    request.form.get('synopsis',''),
            'genre':       request.form.get('genre',''),
            'year':        request.form.get('year') or None,
            'cover_color': request.form.get('cover_color','#7c6f64'),
            'cover_image': request.form.get('cover_image','').strip() or None,
        }
        req.put(f'{API}/api/books/{bid}', json=payload)
        flash('Libro actualizado correctamente.', 'success')
        return redirect(url_for('admin'))
    return render_template('book_form.html', book=book, action='Editar')

@app.route('/admin/book/delete/<int:bid>', methods=['POST'])
@admin_required
def delete_book(bid):
    req.delete(f'{API}/api/books/{bid}')
    flash('Libro eliminado.', 'success')
    return redirect(url_for('admin'))

# ── Auth ──────────────────────────────────────────────────────────────────────
@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'user_id' in session:
        return redirect(url_for('index'))
    if request.method == 'POST':
        r = req.post(f'{API}/api/login', json={
            'username': request.form['username'],
            'password': request.form['password']
        })
        if r.status_code == 200:
            user = r.json()['user']
            session['user_id']  = user['id']
            session['username'] = user['username']
            session['is_admin'] = bool(user['is_admin'])
            flash(f'¡Bienvenido, {user["username"]}!', 'success')
            return redirect(url_for('index'))
        flash(r.json().get('error', 'Error al iniciar sesión'), 'error')
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if 'user_id' in session:
        return redirect(url_for('index'))
    if request.method == 'POST':
        r = req.post(f'{API}/api/register', json={
            'username': request.form['username'].strip(),
            'email':    request.form['email'].strip(),
            'password': request.form['password']
        })
        if r.status_code == 201:
            user = r.json()['user']
            session['user_id']  = user['id']
            session['username'] = user['username']
            session['is_admin'] = False
            flash('¡Cuenta creada! Bienvenido a Bookshelf.', 'success')
            return redirect(url_for('index'))
        flash(r.json().get('error', 'Error al registrarse'), 'error')
    return render_template('register.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('Has cerrado sesión correctamente.', 'info')
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=False)

from flask import Flask, request, jsonify
import mysql.connector
import hashlib
import os
import time
import logging
import re
from functools import wraps
from collections import defaultdict

app = Flask(__name__)

# ── Logging de seguridad ──────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s'
)
logger = logging.getLogger(__name__)

# ── Configuración MySQL ───────────────────────────────────────────────────────
DB_CONFIG = {
    'host':     os.environ.get('DB_HOST',     'localhost'),
    'user':     os.environ.get('DB_USER',     'root'),
    'password': os.environ.get('DB_PASSWORD', ''),
    'database': os.environ.get('DB_NAME',     'bookshelf'),
    'charset':  'utf8mb4'
}

# ── Rate limiting simple (A04 - OWASP) ───────────────────────────────────────
login_attempts = defaultdict(list)
MAX_ATTEMPTS = 5
WINDOW_SECONDS = 300  # 5 minutos

def check_rate_limit(ip):
    now = time.time()
    attempts = login_attempts[ip]
    # Limpiar intentos fuera de la ventana
    login_attempts[ip] = [t for t in attempts if now - t < WINDOW_SECONDS]
    if len(login_attempts[ip]) >= MAX_ATTEMPTS:
        return False
    login_attempts[ip].append(now)
    return True


# ── Autenticación por token (A01 - OWASP) ────────────────────────────────────
def require_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('X-User-Id')
        if not token or not str(token).strip():
            logger.warning(f"[SEGURIDAD] Acceso sin autenticación a {request.path} desde {request.remote_addr}")
            return jsonify({'ok': False, 'error': 'Autenticación requerida'}), 401
        if not str(token).isdigit():
            return jsonify({'ok': False, 'error': 'Token inválido'}), 401
        try:
            conn = get_db()
            cur = conn.cursor(dictionary=True)
            cur.execute("SELECT id FROM users WHERE id=%s", (int(token),))
            user = cur.fetchone()
            cur.close()
            conn.close()
            if not user:
                return jsonify({'ok': False, 'error': 'Usuario no encontrado'}), 401
        except Exception:
            return jsonify({'ok': False, 'error': 'Error de autenticación'}), 401
        return f(*args, **kwargs)
    return decorated

# ── Cabeceras de seguridad (A05 - OWASP) ─────────────────────────────────────
@app.after_request
def add_security_headers(response):
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
    response.headers['Content-Security-Policy'] = "default-src 'self'"
    return response

def get_db():
    retries = 10
    for i in range(retries):
        try:
            return mysql.connector.connect(**DB_CONFIG)
        except Exception as e:
            if i < retries - 1:
                print(f"[DB] Esperando MySQL... intento {i+1}/{retries}", flush=True)
                time.sleep(3)
            else:
                raise e

# ── Hash con salt (A02 - OWASP) ───────────────────────────────────────────────
def hash_pw(pw):
    # Usamos SHA-256 con salt fijo de entorno para mejorar seguridad
    salt = os.environ.get('PASSWORD_SALT', 'bookshelf_salt_2024')
    return hashlib.sha256((pw + salt).encode()).hexdigest()

# ── Validación de inputs (A03 - OWASP) ───────────────────────────────────────
def validate_username(username):
    return bool(re.match(r'^[a-zA-Z0-9_]{3,40}$', username))

def validate_email(email):
    return bool(re.match(r'^[^@]+@[^@]+\.[^@]+$', email))

def validate_password(password):
    return len(password) >= 6

# ── AUTH ──────────────────────────────────────────────────────────────────────

@app.route('/api/login', methods=['POST'])
def login():
    ip = request.remote_addr

    # A04 - Rate limiting
    if not check_rate_limit(ip):
        logger.warning(f"[SEGURIDAD] Rate limit superado para IP: {ip}")
        return jsonify({'ok': False, 'error': 'Demasiados intentos. Espera 5 minutos.'}), 429

    data     = request.get_json()
    username = data.get('username', '')
    password = data.get('password', '')

    # A03 - Validación básica
    if not username or not password:
        return jsonify({'ok': False, 'error': 'Datos incompletos'}), 400

    conn = get_db()
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT id, username, is_admin FROM users WHERE username=%s AND password=%s",
                (username, hash_pw(password)))
    user = cur.fetchone()
    cur.close()
    conn.close()

    if user:
        logger.info(f"[AUTH] Login correcto: {username} desde {ip}")
        return jsonify({'ok': True, 'user': user}), 200

    logger.warning(f"[AUTH] Login fallido: {username} desde {ip}")
    return jsonify({'ok': False, 'error': 'Usuario o contraseña incorrectos'}), 401

@app.route('/api/register', methods=['POST'])
def register():
    data     = request.get_json()
    username = data.get('username', '').strip()
    email    = data.get('email', '').strip()
    password = data.get('password', '')

    # A03 - Validación de inputs
    if not validate_username(username):
        return jsonify({'ok': False, 'error': 'Nombre de usuario inválido (3-40 caracteres, solo letras, números y _)'}), 400
    if not validate_email(email):
        return jsonify({'ok': False, 'error': 'Email inválido'}), 400
    if not validate_password(password):
        return jsonify({'ok': False, 'error': 'La contraseña debe tener al menos 6 caracteres'}), 400

    try:
        conn = get_db()
        cur = conn.cursor()
        cur.execute("INSERT INTO users (username, email, password) VALUES (%s,%s,%s)",
                    (username, email, hash_pw(password)))
        conn.commit()
        uid = cur.lastrowid
        cur.close()
        conn.close()
        logger.info(f"[AUTH] Nuevo usuario registrado: {username}")
        return jsonify({'ok': True, 'user': {'id': uid, 'username': username, 'is_admin': 0}}), 201
    except Exception:
        return jsonify({'ok': False, 'error': 'El nombre de usuario o email ya existe'}), 409

# ── LIBROS ────────────────────────────────────────────────────────────────────

@app.route('/api/books', methods=['GET'])
def get_books():
    search = request.args.get('q', '').strip()
    genre  = request.args.get('genre', '').strip()

    # A03 - Limitar longitud de búsqueda
    if len(search) > 100:
        search = search[:100]

    conn = get_db()
    cur = conn.cursor(dictionary=True)

    sql = """SELECT b.*, u.username AS added_by
             FROM books b LEFT JOIN users u ON b.created_by = u.id
             WHERE 1=1"""
    params = []
    if search:
        sql += " AND (b.title LIKE %s OR b.author LIKE %s)"
        params += [f'%{search}%', f'%{search}%']
    if genre:
        sql += " AND b.genre = %s"
        params.append(genre)
    sql += " ORDER BY b.orden ASC, b.id DESC"
    cur.execute(sql, params)
    books = cur.fetchall()

    cur.execute("SELECT DISTINCT genre FROM books WHERE genre IS NOT NULL AND genre!='' ORDER BY genre")
    genres = [r['genre'] for r in cur.fetchall()]
    cur.close()
    conn.close()

    for b in books:
        for k, v in b.items():
            if hasattr(v, 'isoformat'):
                b[k] = v.isoformat()

    return jsonify({'books': books, 'genres': genres}), 200

@app.route('/api/books/<int:bid>', methods=['GET'])
def get_book(bid):
    conn = get_db()
    cur = conn.cursor(dictionary=True)
    cur.execute("""SELECT b.*, u.username AS added_by
                   FROM books b LEFT JOIN users u ON b.created_by=u.id
                   WHERE b.id=%s""", (bid,))
    book = cur.fetchone()
    if not book:
        cur.close()
        conn.close()
        return jsonify({'error': 'Libro no encontrado'}), 404

    cur.execute("""SELECT ub.*, u.username
                   FROM user_books ub JOIN users u ON ub.user_id=u.id
                   WHERE ub.book_id=%s AND (ub.comment IS NOT NULL OR ub.rating IS NOT NULL)
                   ORDER BY ub.updated_at DESC""", (bid,))
    reviews = cur.fetchall()

    cur.execute("""SELECT COUNT(*) AS total, AVG(rating) AS avg_r
                   FROM user_books WHERE book_id=%s AND rating IS NOT NULL""", (bid,))
    stats = cur.fetchone()
    cur.close()
    conn.close()

    for k, v in book.items():
        if hasattr(v, 'isoformat'): book[k] = v.isoformat()
    for r in reviews:
        for k, v in r.items():
            if hasattr(v, 'isoformat'): r[k] = v.isoformat()
    if stats:
        if stats.get('avg_r'): stats['avg_r'] = float(stats['avg_r'])

    return jsonify({'book': book, 'reviews': reviews, 'stats': stats}), 200

@app.route('/api/books', methods=['POST'])
@require_auth
def add_book():
    data = request.get_json()

    # A03 - Validación de campos obligatorios
    if not data.get('title') or not data.get('author'):
        return jsonify({'ok': False, 'error': 'Título y autor son obligatorios'}), 400

    conn = get_db()
    cur = conn.cursor()
    cur.execute("""INSERT INTO books (title, author, synopsis, genre, year, cover_color, cover_image, created_by)
                   VALUES (%s,%s,%s,%s,%s,%s,%s,%s)""",
                (data['title'][:200], data['author'][:150],
                 data.get('synopsis','')[:2000], data.get('genre','')[:80],
                 data.get('year') or None,
                 data.get('cover_color','#7c6f64')[:20],
                 data.get('cover_image','') or None,
                 data.get('created_by')))
    conn.commit()
    new_id = cur.lastrowid
    cur.close()
    conn.close()
    logger.info(f"[BOOKS] Libro añadido: {data['title']}")
    return jsonify({'ok': True, 'id': new_id}), 201

@app.route('/api/books/<int:bid>', methods=['PUT'])
@require_auth
def edit_book(bid):
    data = request.get_json()

    if not data.get('title') or not data.get('author'):
        return jsonify({'ok': False, 'error': 'Título y autor son obligatorios'}), 400

    conn = get_db()
    cur = conn.cursor()
    cur.execute("""UPDATE books SET title=%s, author=%s, synopsis=%s, genre=%s,
                   year=%s, cover_color=%s, cover_image=%s WHERE id=%s""",
                (data['title'][:200], data['author'][:150],
                 data.get('synopsis','')[:2000], data.get('genre','')[:80],
                 data.get('year') or None,
                 data.get('cover_color','#7c6f64')[:20],
                 data.get('cover_image','') or None,
                 bid))
    conn.commit()
    cur.close()
    conn.close()
    logger.info(f"[BOOKS] Libro editado: ID {bid}")
    return jsonify({'ok': True}), 200

@app.route('/api/books/<int:bid>', methods=['DELETE'])
@require_auth
def delete_book(bid):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("DELETE FROM user_books WHERE book_id=%s", (bid,))
    cur.execute("DELETE FROM books WHERE id=%s", (bid,))
    conn.commit()
    cur.close()
    conn.close()
    logger.info(f"[BOOKS] Libro eliminado: ID {bid}")
    return jsonify({'ok': True}), 200

# ── USER BOOKS ────────────────────────────────────────────────────────────────

@app.route('/api/user/<int:uid>/books', methods=['GET'])
@require_auth
def get_user_books(uid):
    # A01 - Verificar que el usuario solo accede a sus propios datos
    token = request.headers.get('X-User-Id')
    if int(token) != uid:
        logger.warning(f"[SEGURIDAD] Usuario {token} intentó acceder a datos del usuario {uid}")
        return jsonify({'ok': False, 'error': 'Acceso denegado'}), 403
    conn = get_db()
    cur = conn.cursor(dictionary=True)
    cur.execute("""SELECT b.*, ub.status, ub.rating, ub.liked, ub.comment, ub.updated_at
                   FROM user_books ub JOIN books b ON ub.book_id=b.id
                   WHERE ub.user_id=%s ORDER BY ub.updated_at DESC""", (uid,))
    books = cur.fetchall()
    cur.close()
    conn.close()

    for b in books:
        for k, v in b.items():
            if hasattr(v, 'isoformat'): b[k] = v.isoformat()

    return jsonify({'books': books}), 200

@app.route('/api/user/<int:uid>/books/<int:bid>', methods=['GET'])
def get_user_book(uid, bid):
    conn = get_db()
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT * FROM user_books WHERE user_id=%s AND book_id=%s", (uid, bid))
    ub = cur.fetchone()
    cur.close()
    conn.close()
    if ub:
        for k, v in ub.items():
            if hasattr(v, 'isoformat'): ub[k] = v.isoformat()
    return jsonify({'user_book': ub}), 200

@app.route('/api/user/<int:uid>/books/<int:bid>', methods=['POST'])
@require_auth
def update_user_book(uid, bid):
    data    = request.get_json()
    status  = data.get('status', 'quiero_leer')
    rating  = data.get('rating') or None
    liked   = data.get('liked')
    comment = data.get('comment', '').strip() or None

    # A03 - Validar status
    if status not in ('quiero_leer', 'leyendo', 'leido'):
        return jsonify({'ok': False, 'error': 'Estado inválido'}), 400

    # A03 - Validar rating
    if rating is not None and (int(rating) < 1 or int(rating) > 5):
        return jsonify({'ok': False, 'error': 'Valoración debe ser entre 1 y 5'}), 400

    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT id FROM user_books WHERE user_id=%s AND book_id=%s", (uid, bid))
    if cur.fetchone():
        cur.execute("""UPDATE user_books SET status=%s, rating=%s, liked=%s,
                       comment=%s, updated_at=NOW() WHERE user_id=%s AND book_id=%s""",
                    (status, rating, liked, comment, uid, bid))
    else:
        cur.execute("""INSERT INTO user_books (user_id,book_id,status,rating,liked,comment)
                       VALUES (%s,%s,%s,%s,%s,%s)""",
                    (uid, bid, status, rating, liked, comment))
    conn.commit()
    cur.close()
    conn.close()
    return jsonify({'ok': True}), 200

# ── Health check ──────────────────────────────────────────────────────────────
@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok'}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)

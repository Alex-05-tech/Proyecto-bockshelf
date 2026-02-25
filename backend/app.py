from flask import Flask, request, jsonify
import mysql.connector
import hashlib
import os
import time

app = Flask(__name__)

# ── Configuración MySQL ───────────────────────────────────────────────────────
DB_CONFIG = {
    'host':     os.environ.get('DB_HOST',     'localhost'),
    'user':     os.environ.get('DB_USER',     'root'),
    'password': os.environ.get('DB_PASSWORD', ''),
    'database': os.environ.get('DB_NAME',     'bookshelf'),
    'charset':  'utf8mb4'
}

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

def hash_pw(pw):
    return hashlib.sha256(pw.encode()).hexdigest()

# ── AUTH ──────────────────────────────────────────────────────────────────────

@app.route('/api/login', methods=['POST'])
def login():
    data     = request.get_json()
    username = data.get('username', '')
    password = data.get('password', '')
    conn = get_db(); cur = conn.cursor(dictionary=True)
    cur.execute("SELECT id, username, is_admin FROM users WHERE username=%s AND password=%s",
                (username, hash_pw(password)))
    user = cur.fetchone(); cur.close(); conn.close()
    if user:
        return jsonify({'ok': True,  'user': user}), 200
    return jsonify({'ok': False, 'error': 'Usuario o contraseña incorrectos'}), 401

@app.route('/api/register', methods=['POST'])
def register():
    data     = request.get_json()
    username = data.get('username', '').strip()
    email    = data.get('email', '').strip()
    password = hash_pw(data.get('password', ''))
    try:
        conn = get_db(); cur = conn.cursor()
        cur.execute("INSERT INTO users (username, email, password) VALUES (%s,%s,%s)",
                    (username, email, password))
        conn.commit()
        uid = cur.lastrowid
        cur.close(); conn.close()
        return jsonify({'ok': True, 'user': {'id': uid, 'username': username, 'is_admin': 0}}), 201
    except Exception:
        return jsonify({'ok': False, 'error': 'El nombre de usuario o email ya existe'}), 409

# ── LIBROS ────────────────────────────────────────────────────────────────────

@app.route('/api/books', methods=['GET'])
def get_books():
    search = request.args.get('q', '').strip()
    genre  = request.args.get('genre', '').strip()
    conn = get_db(); cur = conn.cursor(dictionary=True)

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
    cur.close(); conn.close()

    # Convertir tipos no serializables
    for b in books:
        for k, v in b.items():
            if hasattr(v, 'isoformat'):
                b[k] = v.isoformat()

    return jsonify({'books': books, 'genres': genres}), 200

@app.route('/api/books/<int:bid>', methods=['GET'])
def get_book(bid):
    conn = get_db(); cur = conn.cursor(dictionary=True)
    cur.execute("""SELECT b.*, u.username AS added_by
                   FROM books b LEFT JOIN users u ON b.created_by=u.id
                   WHERE b.id=%s""", (bid,))
    book = cur.fetchone()
    if not book:
        cur.close(); conn.close()
        return jsonify({'error': 'Libro no encontrado'}), 404

    cur.execute("""SELECT ub.*, u.username
                   FROM user_books ub JOIN users u ON ub.user_id=u.id
                   WHERE ub.book_id=%s AND (ub.comment IS NOT NULL OR ub.rating IS NOT NULL)
                   ORDER BY ub.updated_at DESC""", (bid,))
    reviews = cur.fetchall()

    cur.execute("""SELECT COUNT(*) AS total, AVG(rating) AS avg_r
                   FROM user_books WHERE book_id=%s AND rating IS NOT NULL""", (bid,))
    stats = cur.fetchone()

    cur.close(); conn.close()

    # Convertir tipos no serializables
    for k, v in book.items():
        if hasattr(v, 'isoformat'): book[k] = v.isoformat()
    for r in reviews:
        for k, v in r.items():
            if hasattr(v, 'isoformat'): r[k] = v.isoformat()
    if stats:
        if stats.get('avg_r'): stats['avg_r'] = float(stats['avg_r'])

    return jsonify({'book': book, 'reviews': reviews, 'stats': stats}), 200

@app.route('/api/books', methods=['POST'])
def add_book():
    data = request.get_json()
    conn = get_db(); cur = conn.cursor()
    cur.execute("""INSERT INTO books (title, author, synopsis, genre, year, cover_color, cover_image, created_by)
                   VALUES (%s,%s,%s,%s,%s,%s,%s,%s)""",
                (data['title'], data['author'],
                 data.get('synopsis',''), data.get('genre',''),
                 data.get('year') or None,
                 data.get('cover_color','#7c6f64'),
                 data.get('cover_image','') or None,
                 data.get('created_by')))
    conn.commit()
    new_id = cur.lastrowid
    cur.close(); conn.close()
    return jsonify({'ok': True, 'id': new_id}), 201

@app.route('/api/books/<int:bid>', methods=['PUT'])
def edit_book(bid):
    data = request.get_json()
    conn = get_db(); cur = conn.cursor()
    cur.execute("""UPDATE books SET title=%s, author=%s, synopsis=%s, genre=%s,
                   year=%s, cover_color=%s, cover_image=%s WHERE id=%s""",
                (data['title'], data['author'],
                 data.get('synopsis',''), data.get('genre',''),
                 data.get('year') or None,
                 data.get('cover_color','#7c6f64'),
                 data.get('cover_image','') or None,
                 bid))
    conn.commit(); cur.close(); conn.close()
    return jsonify({'ok': True}), 200

@app.route('/api/books/<int:bid>', methods=['DELETE'])
def delete_book(bid):
    conn = get_db(); cur = conn.cursor()
    cur.execute("DELETE FROM user_books WHERE book_id=%s", (bid,))
    cur.execute("DELETE FROM books WHERE id=%s", (bid,))
    conn.commit(); cur.close(); conn.close()
    return jsonify({'ok': True}), 200

# ── USER BOOKS ────────────────────────────────────────────────────────────────

@app.route('/api/user/<int:uid>/books', methods=['GET'])
def get_user_books(uid):
    conn = get_db(); cur = conn.cursor(dictionary=True)
    cur.execute("""SELECT b.*, ub.status, ub.rating, ub.liked, ub.comment, ub.updated_at
                   FROM user_books ub JOIN books b ON ub.book_id=b.id
                   WHERE ub.user_id=%s ORDER BY ub.updated_at DESC""", (uid,))
    books = cur.fetchall()
    cur.close(); conn.close()

    for b in books:
        for k, v in b.items():
            if hasattr(v, 'isoformat'): b[k] = v.isoformat()

    return jsonify({'books': books}), 200

@app.route('/api/user/<int:uid>/books/<int:bid>', methods=['GET'])
def get_user_book(uid, bid):
    conn = get_db(); cur = conn.cursor(dictionary=True)
    cur.execute("SELECT * FROM user_books WHERE user_id=%s AND book_id=%s", (uid, bid))
    ub = cur.fetchone()
    cur.close(); conn.close()
    if ub:
        for k, v in ub.items():
            if hasattr(v, 'isoformat'): ub[k] = v.isoformat()
    return jsonify({'user_book': ub}), 200

@app.route('/api/user/<int:uid>/books/<int:bid>', methods=['POST'])
def update_user_book(uid, bid):
    data    = request.get_json()
    status  = data.get('status', 'quiero_leer')
    rating  = data.get('rating') or None
    liked   = data.get('liked')
    comment = data.get('comment', '').strip() or None

    conn = get_db(); cur = conn.cursor()
    cur.execute("SELECT id FROM user_books WHERE user_id=%s AND book_id=%s", (uid, bid))
    if cur.fetchone():
        cur.execute("""UPDATE user_books SET status=%s, rating=%s, liked=%s,
                       comment=%s, updated_at=NOW() WHERE user_id=%s AND book_id=%s""",
                    (status, rating, liked, comment, uid, bid))
    else:
        cur.execute("""INSERT INTO user_books (user_id,book_id,status,rating,liked,comment)
                       VALUES (%s,%s,%s,%s,%s,%s)""",
                    (uid, bid, status, rating, liked, comment))
    conn.commit(); cur.close(); conn.close()
    return jsonify({'ok': True}), 200

# ── Health check ──────────────────────────────────────────────────────────────
@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok'}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)

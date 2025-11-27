import sqlite3
from datetime import datetime
from typing import Optional, List, Tuple

DB_PATH = "store.db"


def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_conn()
    cur = conn.cursor()

    # Users
    cur.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        tg_id INTEGER UNIQUE,
        username TEXT,
        full_name TEXT,
        joined_at TEXT,
        badge TEXT DEFAULT NULL,
        total_orders INTEGER DEFAULT 0,
        completed_orders INTEGER DEFAULT 0,
        pending_orders INTEGER DEFAULT 0
    )
    """)

    # Settings (single row)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS settings (
        id INTEGER PRIMARY KEY CHECK (id = 1),
        bot_on INTEGER DEFAULT 1,
        mega_offer TEXT DEFAULT NULL,
        tutorial TEXT DEFAULT NULL,
        off_message TEXT DEFAULT NULL,
        on_message TEXT DEFAULT NULL
    )
    """)
    cur.execute("INSERT OR IGNORE INTO settings (id) VALUES (1)")

    # Categories
    cur.execute("""
    CREATE TABLE IF NOT EXISTS categories (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL
    )
    """)

    # Products
    cur.execute("""
    CREATE TABLE IF NOT EXISTS products (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        category_id INTEGER NOT NULL,
        name TEXT NOT NULL,
        duration TEXT,
        price INTEGER NOT NULL,
        active INTEGER DEFAULT 1,
        stock_limit INTEGER DEFAULT 0,
        FOREIGN KEY (category_id) REFERENCES categories(id)
    )
    """)

    # Stock (accounts)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS stock (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        product_id INTEGER NOT NULL,
        email TEXT NOT NULL,
        password TEXT NOT NULL,
        used INTEGER DEFAULT 0,
        used_at TEXT,
        created_at TEXT,
        FOREIGN KEY (product_id) REFERENCES products(id)
    )
    """)

    # Coupons
    cur.execute("""
    CREATE TABLE IF NOT EXISTS coupons (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        code TEXT UNIQUE,
        discount INTEGER NOT NULL,
        expires_at TEXT,
        product_id INTEGER, -- NULL = all products
        max_uses INTEGER DEFAULT 1,
        used_count INTEGER DEFAULT 0
    )
    """)

    # Orders
    cur.execute("""
    CREATE TABLE IF NOT EXISTS orders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        order_code TEXT UNIQUE,
        user_id INTEGER NOT NULL,
        product_id INTEGER NOT NULL,
        status TEXT NOT NULL, -- draft, pending_admin, approved, rejected, cancelled
        payment_method TEXT,
        original_price INTEGER,
        discount INTEGER DEFAULT 0,
        final_price INTEGER,
        coupon_code TEXT,
        sender_number TEXT,
        txid TEXT,
        created_at TEXT,
        updated_at TEXT,
        remind_count INTEGER DEFAULT 0,
        last_remind_at TEXT,
        FOREIGN KEY (user_id) REFERENCES users(id),
        FOREIGN KEY (product_id) REFERENCES products(id)
    )
    """)

    conn.commit()
    conn.close()


def get_or_create_user(tg_id: int, username: Optional[str], full_name: str) -> sqlite3.Row:
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT * FROM users WHERE tg_id = ?", (tg_id,))
    row = cur.fetchone()
    if row:
        conn.close()
        return row
    now = datetime.utcnow().isoformat()
    cur.execute(
        "INSERT INTO users (tg_id, username, full_name, joined_at) VALUES (?,?,?,?)",
        (tg_id, username, full_name, now),
    )
    conn.commit()
    cur.execute("SELECT * FROM users WHERE tg_id = ?", (tg_id,))
    row = cur.fetchone()
    conn.close()
    return row


def get_settings() -> sqlite3.Row:
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT * FROM settings WHERE id = 1")
    row = cur.fetchone()
    conn.close()
    return row


def set_bot_on(on: bool):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("UPDATE settings SET bot_on = ? WHERE id = 1", (1 if on else 0,))
    conn.commit()
    conn.close()


def set_mega_offer(text: Optional[str]):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("UPDATE settings SET mega_offer = ? WHERE id = 1", (text,))
    conn.commit()
    conn.close()


def set_tutorial(text: Optional[str]):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("UPDATE settings SET tutorial = ? WHERE id = 1", (text,))
    conn.commit()
    conn.close()


def add_category(name: str) -> int:
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("INSERT INTO categories (name) VALUES (?)", (name,))
    conn.commit()
    cid = cur.lastrowid
    conn.close()
    return cid


def get_categories() -> List[sqlite3.Row]:
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT * FROM categories")
    rows = cur.fetchall()
    conn.close()
    return rows


def add_product(category_id: int, name: str, duration: str, price: int) -> int:
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO products (category_id, name, duration, price) VALUES (?,?,?,?)",
        (category_id, name, duration, price),
    )
    conn.commit()
    pid = cur.lastrowid
    conn.close()
    return pid


def get_products_by_category(category_id: int) -> List[sqlite3.Row]:
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        "SELECT p.*, "
        "(SELECT COUNT(*) FROM stock s WHERE s.product_id = p.id AND s.used = 0) AS stock_count "
        "FROM products p WHERE p.category_id = ? AND p.active = 1",
        (category_id,),
    )
    rows = cur.fetchall()
    conn.close()
    return rows


def get_product(product_id: int) -> Optional[sqlite3.Row]:
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        "SELECT p.*, "
        "(SELECT COUNT(*) FROM stock s WHERE s.product_id = p.id AND s.used = 0) AS stock_count "
        "FROM products p WHERE p.id = ?",
        (product_id,),
    )
    row = cur.fetchone()
    conn.close()
    return row


def add_stock(product_id: int, email: str, password: str):
    conn = get_conn()
    cur = conn.cursor()
    now = datetime.utcnow().isoformat()
    cur.execute(
        "INSERT INTO stock (product_id, email, password, created_at) VALUES (?,?,?,?)",
        (product_id, email, password, now),
    )
    conn.commit()
    conn.close()


def get_next_stock(product_id: int) -> Optional[sqlite3.Row]:
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        "SELECT * FROM stock WHERE product_id = ? AND used = 0 ORDER BY id ASC LIMIT 1",
        (product_id,),
    )
    row = cur.fetchone()
    conn.close()
    return row


def mark_stock_used(stock_id: int):
    conn = get_conn()
    cur = conn.cursor()
    now = datetime.utcnow().isoformat()
    cur.execute(
        "UPDATE stock SET used = 1, used_at = ? WHERE id = ?",
        (now, stock_id),
    )
    conn.commit()
    conn.close()


def create_coupon(code: str, discount: int, expires_at: str, product_id: Optional[int], max_uses: int = 1):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO coupons (code, discount, expires_at, product_id, max_uses) VALUES (?,?,?,?,?)",
        (code, discount, expires_at, product_id, max_uses),
    )
    conn.commit()
    conn.close()


def validate_coupon(code: str, product_id: int, now: datetime) -> Tuple[bool, Optional[sqlite3.Row], str]:
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT * FROM coupons WHERE code = ?", (code,))
    row = cur.fetchone()
    if not row:
        conn.close()
        return False, None, "INVALID"
    expires_at = row["expires_at"]
    if expires_at:
        exp = datetime.strptime(expires_at, "%d-%m-%Y %I:%M %p")
        if now > exp:
            conn.close()
            return False, None, "EXPIRED"
    if row["used_count"] >= row["max_uses"]:
        conn.close()
        return False, None, "USED"
    if row["product_id"] is not None and row["product_id"] != product_id:
        conn.close()
        return False, None, "WRONG_PRODUCT"
    conn.close()
    return True, row, "OK"


def mark_coupon_used(coupon_id: int):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        "UPDATE coupons SET used_count = used_count + 1 WHERE id = ?",
        (coupon_id,),
    )
    conn.commit()
    conn.close()


def create_order(user_id: int, product_id: int, price: int) -> int:
    conn = get_conn()
    cur = conn.cursor()
    now = datetime.utcnow().isoformat()
    cur.execute(
        "INSERT INTO orders (order_code, user_id, product_id, status, "
        "original_price, final_price, created_at, updated_at) "
        "VALUES (NULL,?,?,?,?,?,?,?)",
        ("draft", user_id, product_id, "draft", price, price, now, now),
    )
    oid = cur.lastrowid
    # set order_code
    order_code = f"{oid:04d}"
    cur.execute("UPDATE orders SET order_code = ? WHERE id = ?", (order_code, oid))
    conn.commit()
    conn.close()
    return oid


def update_order_payment(
    order_id: int,
    payment_method: str,
    sender: str,
    amount: int,
    txid: str,
    status: str = "pending_admin",
):
    conn = get_conn()
    cur = conn.cursor()
    now = datetime.utcnow().isoformat()
    cur.execute(
        "UPDATE orders SET payment_method = ?, sender_number = ?, final_price = ?, "
        "txid = ?, status = ?, updated_at = ? WHERE id = ?",
        (payment_method, sender, amount, txid, status, now, order_id),
    )
    conn.commit()
    conn.close()


def update_order_coupon(order_id: int, coupon_code: str, discount: int, final_price: int):
    conn = get_conn()
    cur = conn.cursor()
    now = datetime.utcnow().isoformat()
    cur.execute(
        "UPDATE orders SET coupon_code = ?, discount = ?, final_price = ?, updated_at = ? WHERE id = ?",
        (coupon_code, discount, final_price, now, order_id),
    )
    conn.commit()
    conn.close()


def set_order_status(order_id: int, status: str):
    conn = get_conn()
    cur = conn.cursor()
    now = datetime.utcnow().isoformat()
    cur.execute(
        "UPDATE orders SET status = ?, updated_at = ? WHERE id = ?",
        (status, now, order_id),
    )
    conn.commit()
    conn.close()


def get_order(order_id: int) -> Optional[sqlite3.Row]:
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT * FROM orders WHERE id = ?", (order_id,))
    row = cur.fetchone()
    conn.close()
    return row


def get_orders_by_user(user_id: int, status_filter: Optional[str] = None) -> List[sqlite3.Row]:
    conn = get_conn()
    cur = conn.cursor()
    if status_filter:
        cur.execute(
            "SELECT * FROM orders WHERE user_id = ? AND status = ? ORDER BY id DESC",
            (user_id, status_filter),
        )
    else:
        cur.execute(
            "SELECT * FROM orders WHERE user_id = ? ORDER BY id DESC",
            (user_id,),
        )
    rows = cur.fetchall()
    conn.close()
    return rows


def get_pending_orders() -> List[sqlite3.Row]:
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT * FROM orders WHERE status = 'pending_admin' ORDER BY id DESC")
    rows = cur.fetchall()
    conn.close()
    return rows


def users_count() -> int:
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM users")
    n = cur.fetchone()[0]
    conn.close()
    return n

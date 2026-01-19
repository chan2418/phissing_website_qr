# admin_fix.py
import sqlite3
from werkzeug.security import generate_password_hash
from datetime import datetime

DB = "app.db"

ADMIN_USERNAME = "manigandan"
ADMIN_EMAIL = "manigandan.mca2024@adhiyamaan.in"
ADMIN_PASSWORD = "boopathi123456"

def ensure_columns(conn):
    cur = conn.cursor()
    cur.execute("PRAGMA table_info(users)")
    cols = {r[1] for r in cur.fetchall()}
    alters = []
    if "is_admin" not in cols:
        alters.append("ALTER TABLE users ADD COLUMN is_admin INTEGER DEFAULT 0")
    if "login_count" not in cols:
        alters.append("ALTER TABLE users ADD COLUMN login_count INTEGER DEFAULT 0")
    if "last_login" not in cols:
        alters.append("ALTER TABLE users ADD COLUMN last_login TIMESTAMP")
    for sql in alters:
        try:
            cur.execute(sql)
            print("Executed:", sql)
        except Exception as e:
            print("Skip (probably exists):", sql, "->", e)
    conn.commit()

def unique_username(conn, base):
    """Find a free username like base, base_1, base_2..."""
    cur = conn.cursor()
    candidate = base
    i = 1
    while True:
        cur.execute("SELECT 1 FROM users WHERE username = ?", (candidate,))
        if cur.fetchone() is None:
            return candidate
        candidate = f"{base}_{i}"
        i += 1

def promote_admin(conn):
    cur = conn.cursor()
    hashed = generate_password_hash(ADMIN_PASSWORD)

    # Lookup by username and by email
    cur.execute("SELECT * FROM users WHERE username = ?", (ADMIN_USERNAME,))
    row_u = cur.fetchone()
    cur.execute("SELECT * FROM users WHERE email = ?", (ADMIN_EMAIL,))
    row_e = cur.fetchone()

    if row_u is None and row_e is None:
        # Create fresh admin
        cur.execute(
            "INSERT INTO users (username, email, password_hash, is_admin, created_at) VALUES (?, ?, ?, ?, ?)",
            (ADMIN_USERNAME, ADMIN_EMAIL, hashed, 1, datetime.utcnow())
        )
        print("Created new admin:", ADMIN_USERNAME)
        conn.commit()
        return

    if row_e is not None and row_u is None:
        # Email exists; ensure this row uses the desired username
        uid = row_e["id"]
        # If some other row already has the desired username, rename that other row first
        cur.execute("SELECT id FROM users WHERE username = ?", (ADMIN_USERNAME,))
        other = cur.fetchone()
        if other and other["id"] != uid:
            new_name = unique_username(conn, ADMIN_USERNAME + "_old")
            cur.execute("UPDATE users SET username = ? WHERE id = ?", (new_name, other["id"]))
            print(f"Renamed existing '{ADMIN_USERNAME}' to '{new_name}' to free the username.")
        # Now set username, hash, admin on the email row
        cur.execute(
            "UPDATE users SET username = ?, password_hash = ?, is_admin = 1 WHERE id = ?",
            (ADMIN_USERNAME, hashed, uid)
        )
        print(f"Promoted email '{ADMIN_EMAIL}' row to admin with username '{ADMIN_USERNAME}'.")
        conn.commit()
        return

    if row_u is not None and row_e is None:
        # Username exists; attach desired email
        uid = row_u["id"]
        cur.execute(
            "UPDATE users SET email = ?, password_hash = ?, is_admin = 1 WHERE id = ?",
            (ADMIN_EMAIL, hashed, uid)
        )
        print(f"Updated user '{ADMIN_USERNAME}' with email '{ADMIN_EMAIL}' and admin rights.")
        conn.commit()
        return

    # Both exist
    if row_u["id"] == row_e["id"]:
        # Same row: just ensure admin + password
        uid = row_u["id"]
        cur.execute(
            "UPDATE users SET password_hash = ?, is_admin = 1 WHERE id = ?",
            (hashed, uid)
        )
        print(f"Refreshed password and admin rights for '{ADMIN_USERNAME}'.")
        conn.commit()
        return
    else:
        # Different rows: make the email row the canonical admin,
        # and free up the username by renaming the username row.
        uid_email = row_e["id"]
        uid_user = row_u["id"]
        new_name = unique_username(conn, ADMIN_USERNAME + "_old")
        cur.execute("UPDATE users SET username = ? WHERE id = ?", (new_name, uid_user))
        print(f"Renamed conflicting username row '{ADMIN_USERNAME}' -> '{new_name}'.")
        cur.execute(
            "UPDATE users SET username = ?, password_hash = ?, is_admin = 1 WHERE id = ?",
            (ADMIN_USERNAME, hashed, uid_email)
        )
        print(f"Assigned username '{ADMIN_USERNAME}' to the email row and granted admin.")
        conn.commit()

def show_users(conn, title):
    print("\n" + title)
    cur = conn.cursor()
    try:
        cur.execute("SELECT id, username, email, is_admin, login_count, last_login, created_at FROM users ORDER BY id")
        for r in cur.fetchall():
            print(dict(r))
    except Exception as e:
        print("Error listing users:", e)

def main():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    ensure_columns(conn)
    show_users(conn, "Before:")
    promote_admin(conn)
    show_users(conn, "After:")
    conn.close()
    print("\nDone. Try logging in with:")
    print(f"  username: {ADMIN_USERNAME}")
    print(f"  password: {ADMIN_PASSWORD}")

if __name__ == "__main__":
    main()

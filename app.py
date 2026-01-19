from flask import(
    Flask,
    request,
    render_template,
    redirect,
    url_for,
    flash,
    session,
    has_app_context,
    g,
    Response,
    abort,
)
from flask_mail import Mail, Message
import numpy as np
import pandas as pd
import warnings
import pickle
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
from feature import FeatureExtraction
import random
import string
import secrets
import csv
from io import StringIO
import os
from PIL import Image
from pyzbar.pyzbar import decode


warnings.filterwarnings("ignore")

# ------------------ ML MODEL ------------------
with open("model.pkl", "rb") as file:
    gbc = pickle.load(file)

# ------------------ APP CONFIG ------------------
app = Flask(__name__)
app.secret_key = "supersecret123"
app.permanent_session_lifetime = timedelta(days=7)

# ------------------ MAIL CONFIG ------------------
app.config["MAIL_SERVER"] = "smtp.gmail.com"
app.config["MAIL_PORT"] = 587
app.config["MAIL_USE_TLS"] = True
app.config["MAIL_USERNAME"] = "hemavathi2661998@gmail.com"
app.config["MAIL_PASSWORD"] = "mwey ryir egob obhc"   # Gmail app password
app.config["MAIL_DEFAULT_SENDER"] = app.config["MAIL_USERNAME"]

mail = Mail(app)

# ------------------ DB HELPERS ------------------
DB_PATH = "app.db"
UPLOAD_FOLDER = "static/uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER



def get_db():
    if has_app_context():
        db = getattr(g, "_db", None)
        if db is None:
            db = g._db = sqlite3.connect(DB_PATH)
            db.row_factory = sqlite3.Row
        return db
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


@app.teardown_appcontext
def close_db(exception):
    db = g.pop("_db", None)
    if db:
        db.close()

def extract_url_from_qr(image_path):
    img = Image.open(image_path)
    decoded_objects = decode(img)
    if decoded_objects:
        print("--------------",decoded_objects[0].data.decode("utf-8"))
        return decoded_objects[0].data.decode("utf-8")
    return None

# ------------------ INIT DB ------------------
def init_db():
    with get_db() as db:
        # --- main users table ---
        db.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE,
                password_hash TEXT NOT NULL,
                is_admin INTEGER DEFAULT 0,
                login_count INTEGER DEFAULT 0,
                last_login TEXT,
                created_at TEXT DEFAULT (datetime('now')),
                is_verified INTEGER DEFAULT 1
            )
        """
        )

        # --- pending verification (OTP flow) ---
        db.execute(
            """
            CREATE TABLE IF NOT EXISTS pending_users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                otp_code TEXT NOT NULL,
                otp_expires TEXT NOT NULL,
                created_at TEXT DEFAULT (datetime('now'))
            )
        """
        )

        # --- url checks history ---
        db.execute(
            """
            CREATE TABLE IF NOT EXISTS url_checks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                username TEXT,
                url TEXT NOT NULL,
                label TEXT NOT NULL,
                probability REAL,
                created_at TEXT NOT NULL DEFAULT (datetime('now')),
                FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE SET NULL
            )
        """
        )

        db.execute(
            """
            CREATE TABLE IF NOT EXISTS password_resets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                token TEXT UNIQUE NOT NULL,
                expires_at TEXT NOT NULL,
                created_at TEXT DEFAULT (datetime('now')),
                FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
            )
        """
        )

        db.execute(
            "CREATE INDEX IF NOT EXISTS idx_pwreset_token ON password_resets(token)"
        )
        db.execute(
            "CREATE INDEX IF NOT EXISTS idx_pwreset_exp ON password_resets(expires_at)"
        )
        db.execute(
            "CREATE INDEX IF NOT EXISTS idx_url_checks_created_at ON url_checks(created_at DESC)"
        )
        db.execute(
            "CREATE INDEX IF NOT EXISTS idx_url_checks_username ON url_checks(username)"
        )
        db.execute(
            "CREATE INDEX IF NOT EXISTS idx_users_username ON users(username)"
        )
        db.execute(
            "CREATE INDEX IF NOT EXISTS idx_users_last_login ON users(last_login)"
        )

        # default admin (idempotent)
        admin_username = "manigandan"
        admin_email = "manigandan.mca2024@adhiyamaan.in"
        admin_password = "boopathi123456"
        try:
            db.execute(
                """
                INSERT INTO users (username, email, password_hash, is_admin, is_verified)
                VALUES (?, ?, ?, 1, 1)
                """,
                (admin_username, admin_email, generate_password_hash(admin_password)),
            )
        except sqlite3.IntegrityError:
            db.execute(
                "UPDATE users SET is_admin = 1, is_verified = 1 WHERE username = ?",
                (admin_username,),
            )


with app.app_context():
    init_db()

# ------------------ HELPERS ------------------
def generate_otp():
    return "".join(random.choices(string.digits, k=6))


def send_otp_email(email, uname, otp):
    msg = Message("Your Verification Code", recipients=[email])
    msg.body = (
        f"Hello {uname},\n\n"
        f"Your verification code is: {otp}\n"
        f"This code expires in 5 minutes.\n\n"
        f"- Phishing Website Detection"
    )
    mail.send(msg)


@app.context_processor
def inject_user():
    username = session.get("username")
    is_admin = False
    if username:
        with get_db() as db:
            u = db.execute(
                "SELECT is_admin FROM users WHERE username=?",
                (username,),
            ).fetchone()
            if u and u["is_admin"] == 1:
                is_admin = True
    return {"current_username": username, "is_admin": is_admin}


def get_user_by_username(uname):
    with get_db() as db:
        return db.execute(
            "SELECT * FROM users WHERE username=?",
            (uname,),
        ).fetchone()


def get_user_by_email(email):
    with get_db() as db:
        return db.execute(
            "SELECT * FROM users WHERE email = ?",
            (email,),
        ).fetchone()


# ------------------ ROUTES ------------------

@app.route("/")
@app.route("/first")
def first():
    return render_template("landing_page.html")


# LOGIN
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        uname = (request.form.get("uname") or "").strip()
        pwd = request.form.get("pwd") or ""
        remember = request.form.get("remember") == "1"

        user = get_user_by_username(uname)

        if not user:
            flash("Invalid username or password", "danger")
            return redirect(url_for("login"))

        if user["is_verified"] == 0:
            flash("Please verify your email first.", "warning")
            session["pending_verify"] = uname
            return redirect(url_for("verify"))

        if check_password_hash(user["password_hash"], pwd):
            session["username"] = user["username"]
            if remember:
                session.permanent = True

            with get_db() as db:
                db.execute(
                    """
                    UPDATE users
                    SET login_count = login_count + 1,
                        last_login = ?
                    WHERE id = ?
                    """,
                    (datetime.utcnow().isoformat(), user["id"]),
                )

            return redirect(url_for("index"))

        flash("Invalid username or password", "danger")
        return redirect(url_for("login"))

    return render_template("auth.html")


# REGISTER
@app.route("/register", methods=["POST"])
def register():
    uname = (request.form.get("uname") or "").strip()
    email = (request.form.get("email") or "").strip().lower()
    pwd = request.form.get("pwd") or ""
    cpwd = request.form.get("cpwd") or ""

    if not uname or not email or not pwd or not cpwd:
        flash("Please fill all fields.", "warning")
        return render_template("auth.html", open_register=True)

    if pwd != cpwd:
        flash("Passwords do not match", "danger")
        return render_template("auth.html", open_register=True)

    pwd_hash = generate_password_hash(pwd)

    with get_db() as db:
        # unique check
        if db.execute(
            "SELECT 1 FROM users WHERE username=? OR email=?",
            (uname, email),
        ).fetchone():
            flash("Username or email already exists", "danger")
            return render_template("auth.html", open_register=True)

        # Directly create verified user (skip email verification)
        db.execute(
            """
            INSERT INTO users (username, email, password_hash, is_verified)
            VALUES (?, ?, ?, 1)
            """,
            (uname, email, pwd_hash),
        )

    flash("Registration successful! Please login.", "success")
    return redirect(url_for("login"))


# VERIFY PAGE (GET)
@app.get("/verify")
def verify():
    uname = session.get("pending_verify")
    if not uname:
        return redirect(url_for("login"))
    return render_template("verify.html", username=uname)


# VERIFY SUBMIT (POST)
@app.post("/verify")
def verify_post():
    uname = session.get("pending_verify")
    if not uname:
        flash("No account pending verification", "warning")
        return redirect(url_for("login"))

    otp_in = request.form.get("otp") or ""

    with get_db() as db:
        pending = db.execute(
            "SELECT * FROM pending_users WHERE username=?",
            (uname,),
        ).fetchone()

        if not pending:
            flash("Account not found. Register again.", "danger")
            return redirect(url_for("login"))

        expiry = datetime.fromisoformat(pending["otp_expires"])
        if datetime.utcnow() > expiry:
            flash("OTP expired. Resend.", "warning")
            return redirect(url_for("verify"))

        if otp_in != pending["otp_code"]:
            flash("Invalid OTP", "danger")
            return redirect(url_for("verify"))

        # create real user
        db.execute(
            """
            INSERT INTO users (username, email, password_hash, is_verified)
            VALUES (?, ?, ?, 1)
            """,
            (pending["username"], pending["email"], pending["password_hash"]),
        )

        db.execute("DELETE FROM pending_users WHERE id=?", (pending["id"],))

    session.pop("pending_verify", None)

    # Show OTP success page
    return render_template("otp_success.html", username=uname)


# RESEND OTP
@app.route("/verify/resend", methods=["POST"])
def verify_resend():
    uname = session.get("pending_verify")
    if not uname:
        flash("No email pending verification.", "warning")
        return redirect(url_for("login"))

    with get_db() as db:
        p = db.execute(
            "SELECT * FROM pending_users WHERE username=?",
            (uname,),
        ).fetchone()

        if not p:
            flash("Account not found. Please register again.", "warning")
            return redirect(url_for("login"))

        otp = generate_otp()
        expires = (datetime.utcnow() + timedelta(minutes=5)).isoformat()

        db.execute(
            "UPDATE pending_users SET otp_code=?, otp_expires=? WHERE id=?",
            (otp, expires, p["id"]),
        )

    try:
        send_otp_email(p["email"], uname, otp)
    except Exception as e:
        print("MAIL ERROR (resend):", e)
        flash(f"Could not resend email. DEV OTP: {otp}", "warning")

    flash("OTP resent!", "success")
    return redirect(url_for("verify"))


# OPTIONAL: direct route for otp-success if you ever link with url_for('otp_success')
@app.route("/otp-success/<username>")
def otp_success(username):
    return render_template("otp_success.html", username=username)


# LOGOUT
@app.route("/logout")
def logout():
    session.pop("username", None)
    flash("You are logged out", "info")
    return redirect(url_for("first"))


# MAIN HOME
@app.route("/index")
def index():
    if "username" not in session:
        flash("Please login first!", "warning")
        return redirect(url_for("login"))
    return render_template("index.html")


# PREDICT
@app.route("/posts", methods=["GET", "POST"])
@app.route("/posts", methods=["GET", "POST"])
def posts():
    if "username" not in session:
        flash("Please login first!", "warning")
        return redirect(url_for("login"))

    if request.method == "POST":
        try:
            if "image" not in request.files:
                flash("No image uploaded", "danger")
                return render_template("result.html", xx=-1)

            file = request.files["image"]
            if file.filename == "":
                flash("Please select an image", "warning")
                return render_template("result.html", xx=-1)

            filepath = os.path.join(app.config["UPLOAD_FOLDER"], file.filename)
            file.save(filepath)

            qr_url = extract_url_from_qr(filepath)
            if not qr_url:
                flash("QR not detected or invalid QR image", "danger")
                return render_template("result.html", xx=-1)

            obj = FeatureExtraction(qr_url)
            x = np.array(obj.getFeaturesList()).reshape(1, 30)

            proba = gbc.predict_proba(x)[0]
            non_phish_prob = float(proba[1])
            label = "safe" if non_phish_prob >= 0.5 else "phishing"

            with get_db() as db:
                db.execute(
                    """
                    INSERT INTO url_checks (username, url, label, probability, created_at)
                    VALUES (?, ?, ?, ?, datetime('now'))
                    """,
                    (session.get("username"), qr_url, label, non_phish_prob),
                )

            return render_template(
                "result.html",
                xx=round(non_phish_prob, 2),
                url=qr_url,
                label=label,
                image_path=filepath
            )

        except Exception as e:
            flash(f"Prediction failed: {e}", "danger")
            return render_template("result.html", xx=-1)

    return render_template("result.html", xx=-1)


# ADMIN
@app.route("/admin")
def admin_dashboard():
    if "username" not in session:
        return redirect(url_for("login"))
    with get_db() as db:
        u = db.execute(
            "SELECT is_admin FROM users WHERE username=?",
            (session["username"],),
        ).fetchone()
        if not u or u["is_admin"] != 1:
            flash("Admin only", "danger")
            return redirect(url_for("index"))

        users = db.execute("SELECT * FROM users").fetchall()
    return render_template("admin.html", users=users)


# DELETE USER AJAX
@app.post("/admin/users/<int:uid>/delete")
def admin_delete(uid):
    if "username" not in session:
        return "AUTH", 401

    with get_db() as db:
        db.execute("DELETE FROM users WHERE id=?", (uid,))
    return "OK", 200


def require_admin():
    if "username" not in session:
        flash("Please login first!", "warning")
        return False

    with get_db() as db:
        user = db.execute(
            "SELECT is_admin FROM users WHERE username = ?",
            (session["username"],),
        ).fetchone()

    if not user or user["is_admin"] != 1:
        flash("Admin access required.", "danger")
        return False

    return True


def get_user_by_id(uid):
    with get_db() as db:
        return db.execute(
            "SELECT * FROM users WHERE id = ?",
            (uid,),
        ).fetchone()


# ---- Admin: user detail ----
@app.route("/admin/user/<int:uid>")
def admin_user_detail(uid):
    if not require_admin():
        return redirect(url_for("login"))

    user = get_user_by_id(uid)
    if not user:
        flash("User not found.", "warning")
        return redirect(url_for("admin_dashboard"))

    return render_template("admin_user.html", user=user)


# ---- Admin: toggle admin permission ----
@app.post("/admin/toggle_admin/<int:uid>")
def admin_toggle_admin(uid):
    if "username" not in session:
        flash("Please login first!", "warning")
        return redirect(url_for("login"))

    with get_db() as db:
        me = db.execute(
            "SELECT id, username, is_admin FROM users WHERE username=?",
            (session["username"],),
        ).fetchone()
        if not me or me["is_admin"] != 1:
            flash("Admin access required.", "danger")
            return redirect(url_for("index"))

        target = db.execute(
            "SELECT id, username, is_admin FROM users WHERE id=?",
            (uid,),
        ).fetchone()
        if not target:
            flash("User not found.", "warning")
            return redirect(url_for("admin_dashboard"))

        if target["username"] == me["username"]:
            flash("You cannot change your own admin status.", "warning")
            return redirect(url_for("admin_dashboard"))

        if target["is_admin"] == 1:
            admins_left = db.execute(
                "SELECT COUNT(*) AS c FROM users WHERE is_admin = 1 AND id <> ?",
                (uid,),
            ).fetchone()["c"]
            if admins_left <= 0:
                flash("Cannot revoke the last remaining admin.", "warning")
                return redirect(url_for("admin_dashboard"))

        new_flag = 0 if target["is_admin"] == 1 else 1
        db.execute(
            "UPDATE users SET is_admin=? WHERE id=?",
            (new_flag, uid),
        )

    flash(f"Updated admin status for '{target['username']}'.", "success")
    return redirect(url_for("admin_dashboard"))


# View my history
@app.route("/history")
def history():
    if "username" not in session:
        flash("Please login first!", "warning")
        return redirect(url_for("login"))
    with get_db() as db:
        rows = db.execute(
            """
            SELECT id, url, label, probability, username, created_at
            FROM url_checks
            WHERE username = ?
            ORDER BY datetime(created_at) DESC
            """,
            (session["username"],),
        ).fetchall()
    return render_template("history.html", rows=rows, scope="mine")


# Admin: view all users history
@app.route("/admin/history")
def admin_history():
    if "username" not in session:
        flash("Please login first!", "warning")
        return redirect(url_for("login"))
    with get_db() as db:
        me = db.execute(
            "SELECT is_admin FROM users WHERE username=?",
            (session["username"],),
        ).fetchone()
        if not me or me["is_admin"] != 1:
            flash("Admin access required.", "danger")
            return redirect(url_for("index"))

        rows = db.execute(
            """
            SELECT id, url, label, probability, username, created_at
            FROM url_checks
            ORDER BY datetime(created_at) DESC
            """
        ).fetchall()
    return render_template("history.html", rows=rows, scope="all")


@app.route("/history.csv")
def history_csv():
    if "username" not in session:
        flash("Please login first!", "warning")
        return redirect(url_for("login"))

    see_all = request.args.get("all") == "1"
    with get_db() as db:
        if see_all:
            me = db.execute(
                "SELECT is_admin FROM users WHERE username=?",
                (session["username"],),
            ).fetchone()
            if not me or me["is_admin"] != 1:
                abort(403)
            rows = db.execute(
                """
                SELECT username, url, label, probability, created_at
                FROM url_checks
                ORDER BY datetime(created_at) DESC
                """
            ).fetchall()
        else:
            rows = db.execute(
                """
                SELECT username, url, label, probability, created_at
                FROM url_checks
                WHERE username = ?
                ORDER BY datetime(created_at) DESC
                """,
                (session["username"],),
            ).fetchall()

    si = StringIO()
    writer = csv.writer(si)
    writer.writerow(
        ["username", "url", "label", "probability_non_phish", "timestamp_utc"]
    )
    for r in rows:
        writer.writerow(
            [
                r["username"],
                r["url"],
                r["label"],
                f"{(r['probability'] or 0):.4f}",
                r["created_at"],
            ]
        )
    output = si.getvalue()

    return Response(
        output,
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment;filename=history.csv"},
    )


# ------------------ PASSWORD RESET HELPERS ------------------
def create_password_reset(user_id, minutes_valid=30):
    token = secrets.token_urlsafe(32)
    expires = (datetime.utcnow() + timedelta(minutes=minutes_valid)).isoformat()
    with get_db() as db:
        db.execute(
            "INSERT INTO password_resets (user_id, token, expires_at) VALUES (?, ?, ?)",
            (user_id, token, expires),
        )
    return token, expires


def find_reset_by_token(token):
    with get_db() as db:
        return db.execute(
            "SELECT * FROM password_resets WHERE token = ?",
            (token,),
        ).fetchone()


def delete_reset_token(token):
    with get_db() as db:
        db.execute(
            "DELETE FROM password_resets WHERE token = ?",
            (token,),
        )


def send_reset_email(email, reset_link):
    msg = Message(
        subject="Reset your password",
        recipients=[email],
        body=(
            f"Click the link to reset your password (valid for 30 minutes):\n"
            f"{reset_link}\n\nIf you didn't request this, ignore this message."
        ),
    )
    mail.send(msg)


# --- Forgot password (request) ---
@app.get("/forgot")
def forgot_get():
    return render_template("forgot.html")


@app.post("/forgot")
def forgot_post():
    email = (request.form.get("email") or "").strip().lower()
    if not email:
        flash("Enter your email.", "warning")
        return redirect(url_for("forgot_get"))

    user = get_user_by_email(email)
    if not user:
        flash("If the email exists, you'll receive a reset link.", "info")
        return redirect(url_for("login"))

    token, _ = create_password_reset(user["id"], minutes_valid=30)
    reset_link = url_for("reset_with_token", token=token, _external=True)
    
    # Display reset link directly instead of emailing (email disabled)
    flash(
        f"Password reset link (valid 30 minutes): {reset_link}",
        "success",
    )
    return redirect(url_for("login"))


# --- Reset password (use token) ---
@app.get("/reset/<token>")
def reset_with_token(token):
    row = find_reset_by_token(token)
    if not row:
        flash("Invalid or expired token.", "danger")
        return redirect(url_for("forgot_get"))

    try:
        exp = datetime.fromisoformat(row["expires_at"])
        if datetime.utcnow() > exp:
            delete_reset_token(token)
            flash("This reset link has expired. Request a new one.", "warning")
            return redirect(url_for("forgot_get"))
    except Exception:
        delete_reset_token(token)
        flash("Invalid token.", "danger")
        return redirect(url_for("forgot_get"))

    return render_template("reset.html", token=token)


@app.post("/reset/<token>")
def reset_with_token_post(token):
    row = find_reset_by_token(token)
    if not row:
        flash("Invalid or expired token.", "danger")
        return redirect(url_for("forgot_get"))

    try:
        exp = datetime.fromisoformat(row["expires_at"])
        if datetime.utcnow() > exp:
            delete_reset_token(token)
            flash("This reset link has expired. Request a new one.", "warning")
            return redirect(url_for("forgot_get"))
    except Exception:
        delete_reset_token(token)
        flash("Invalid token.", "danger")
        return redirect(url_for("forgot_get"))

    pwd = request.form.get("pwd") or ""
    cpwd = request.form.get("cpwd") or ""
    if len(pwd) < 6:
        flash("Password must be at least 6 characters.", "warning")
        return redirect(url_for("reset_with_token", token=token))
    if pwd != cpwd:
        flash("Passwords do not match.", "warning")
        return redirect(url_for("reset_with_token", token=token))

    with get_db() as db:
        db.execute(
            "UPDATE users SET password_hash = ? WHERE id = ?",
            (generate_password_hash(pwd), row["user_id"]),
        )
    delete_reset_token(token)

    flash("Password updated! Please login.", "success")
    return redirect(url_for("login"))


# RUN
if __name__ == "__main__":
    app.run(debug=True)

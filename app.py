import os
import uuid
import sqlite3
from flask import Flask, render_template, request, redirect, url_for, session, send_file, flash, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from storage import upload_file_blob, get_file_blob_path

app = Flask(__name__)
app.secret_key = "cloud-drive-secret-key-raheem-secure"

DB_NAME = "clouddrive.db"

def get_db():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

@app.route("/")
def index():
    if "user_id" not in session:
        return redirect(url_for("login"))
    
    conn = get_db()
    files = conn.execute(
        "SELECT * FROM files WHERE user_id = ? ORDER BY uploaded_at DESC", 
        (session["user_id"],)
    ).fetchall()
    conn.close()
    return render_template("dashboard.html", username=session["username"], files=files)

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()
        
        if not username or not password:
            flash("Please provide both username and password.", "error")
            return render_template("auth.html", mode="register")
        
        conn = get_db()
        try:
            hashed_pw = generate_password_hash(password)
            conn.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, hashed_pw))
            conn.commit()
            flash("Account registered successfully! Please log in.", "success")
            return redirect(url_for("login"))
        except sqlite3.IntegrityError:
            flash("Username already exists. Choose another.", "error")
        finally:
            conn.close()
            
    return render_template("auth.html", mode="register")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()
        
        conn = get_db()
        user = conn.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
        conn.close()
        
        if user and check_password_hash(user["password"], password):
            session["user_id"] = user["id"]
            session["username"] = user["username"]
            return redirect(url_for("index"))
        else:
            flash("Invalid credentials.", "error")
            
    return render_template("auth.html", mode="login")

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

@app.route("/upload", methods=["POST"])
def upload():
    if "user_id" not in session:
        return redirect(url_for("login"))
        
    file = request.files.get("file")
    if not file or file.filename == "":
        flash("No file selected for upload.", "error")
        return redirect(url_for("index"))
        
    orig_name = secure_filename(file.filename)
    unique_key = f"{uuid.uuid4().hex}_{orig_name}"
    share_token = uuid.uuid4().hex[:12]
    content_type = file.content_type or "application/octet-stream"
    
    file.seek(0, os.SEEK_END)
    size = file.tell()
    file.seek(0)
    
    upload_file_blob(file, unique_key)
    
    conn = get_db()
    conn.execute(
        """INSERT INTO files (user_id, filename, file_key, file_size, content_type, share_token)
           VALUES (?, ?, ?, ?, ?, ?)""",
        (session["user_id"], orig_name, unique_key, size, content_type, share_token)
    )
    conn.commit()
    conn.close()
    
    flash("File successfully uploaded to cloud storage!", "success")
    return redirect(url_for("index"))

@app.route("/download/<int:file_id>")
def download(file_id):
    if "user_id" not in session:
        return redirect(url_for("login"))
        
    conn = get_db()
    row = conn.execute("SELECT * FROM files WHERE id = ? AND user_id = ?", (file_id, session["user_id"])).fetchone()
    conn.close()
    
    if not row:
        return "File not found or unauthorized.", 404
        
    local_path = get_file_blob_path(row["file_key"])
    return send_file(local_path, as_attachment=True, download_name=row["filename"])

@app.route("/share/<token>")
def public_share(token):
    conn = get_db()
    row = conn.execute("SELECT * FROM files WHERE share_token = ?", (token,)).fetchone()
    conn.close()
    
    if not row:
        return "Shared link is invalid or expired.", 404
        
    local_path = get_file_blob_path(row["file_key"])
    return send_file(local_path, as_attachment=True, download_name=row["filename"])

@app.route("/delete/<int:file_id>", methods=["POST"])
def delete_file(file_id):
    if "user_id" not in session:
        return redirect(url_for("login"))
        
    conn = get_db()
    row = conn.execute("SELECT * FROM files WHERE id = ? AND user_id = ?", (file_id, session["user_id"])).fetchone()
    if row:
        path = get_file_blob_path(row["file_key"])
        if os.path.exists(path):
            os.remove(path)
        conn.execute("DELETE FROM files WHERE id = ?", (file_id,))
        conn.commit()
        flash("File deleted successfully.", "success")
    conn.close()
    return redirect(url_for("index"))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)

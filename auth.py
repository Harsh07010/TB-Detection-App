from flask import Flask, request, jsonify, Blueprint
import sqlite3

auth_app = Blueprint("auth_app", __name__)
db = "users.db"

def init_db():
    with sqlite3.connect(db) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                email TEXT PRIMARY KEY,
                name TEXT,
                password TEXT
            )
        """)

@auth_app.route("/signup", methods=["POST"])
def signup():
    data = request.json
    with sqlite3.connect(db) as conn:
        try:
            conn.execute("INSERT INTO users (email, name, password) VALUES (?, ?, ?)",
                         (data["email"], data["name"], data["password"]))
            return jsonify({"message": "Signup successful"}), 200
        except sqlite3.IntegrityError:
            return jsonify({"error": "User already exists"}), 409

@auth_app.route("/signin", methods=["POST"])
def signin():
    data = request.json
    with sqlite3.connect(db) as conn:
        user = conn.execute("SELECT * FROM users WHERE email=? AND password=?",
                            (data["email"], data["password"])).fetchone()
        if user:
            return jsonify({"message": "Login successful"}), 200
        else:
            return jsonify({"error": "Invalid credentials"}), 401


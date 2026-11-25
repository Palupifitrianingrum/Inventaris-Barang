"""Inventory API - Flask + MySQL (dipakai Track A dan Track B)."""
import os
import time

import pymysql
from flask import Flask, jsonify, request

app = Flask(__name__)


def get_conn():
    return pymysql.connect(
        host=os.environ["DB_HOST"],
        port=int(os.environ.get("DB_PORT", "3306")),
        user=os.environ["DB_USER"],
        password=os.environ["DB_PASSWORD"],
        database=os.environ.get("DB_NAME", "inventory"),
        cursorclass=pymysql.cursors.DictCursor,
        autocommit=True,
    )


def init_db(retries=10):
    """Buat tabel kalau belum ada. Retry supaya aman saat DB baru menyala."""
    for attempt in range(retries):
        try:
            conn = get_conn()
            with conn.cursor() as cur:
                cur.execute(
                    """CREATE TABLE IF NOT EXISTS items (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        name VARCHAR(100) NOT NULL,
                        quantity INT NOT NULL DEFAULT 0,
                        location VARCHAR(100) NULL
                    )"""
                )
            conn.close()
            return
        except pymysql.MySQLError as exc:
            print(f"DB belum siap ({attempt + 1}/{retries}): {exc}")
            time.sleep(3)
    raise RuntimeError("Tidak bisa terhubung ke database")


def validate(data):
    """Return (clean_dict, error_message)."""
    if not isinstance(data, dict):
        return None, "body harus berupa JSON object"
    name = data.get("name")
    if not isinstance(name, str) or not 1 <= len(name.strip()) <= 100:
        return None, "name wajib diisi (1-100 karakter)"
    quantity = data.get("quantity", 0)
    if isinstance(quantity, bool) or not isinstance(quantity, int) or quantity < 0:
        return None, "quantity harus integer >= 0"
    location = data.get("location")
    if location is not None and (not isinstance(location, str) or len(location) > 100):
        return None, "location maksimal 100 karakter"
    return {"name": name.strip(), "quantity": quantity, "location": location}, None


@app.get("/health")
def health():
    return jsonify({"status": "ok"})


@app.post("/items")
def create_item():
    clean, err = validate(request.get_json(silent=True))
    if err:
        return jsonify({"error": err}), 400
    conn = get_conn()
    with conn.cursor() as cur:
        cur.execute(
            "INSERT INTO items (name, quantity, location) VALUES (%s, %s, %s)",
            (clean["name"], clean["quantity"], clean["location"]),
        )
        clean["id"] = cur.lastrowid
    conn.close()
    return jsonify(clean), 201


@app.get("/items")
def list_items():
    conn = get_conn()
    with conn.cursor() as cur:
        cur.execute("SELECT id, name, quantity, location FROM items ORDER BY id")
        rows = cur.fetchall()
    conn.close()
    return jsonify(rows), 200


@app.put("/items/<int:item_id>")
def update_item(item_id):
    clean, err = validate(request.get_json(silent=True))
    if err:
        return jsonify({"error": err}), 400
    conn = get_conn()
    with conn.cursor() as cur:
        cur.execute("SELECT id FROM items WHERE id = %s", (item_id,))
        if cur.fetchone() is None:
            conn.close()
            return jsonify({"error": "item tidak ditemukan"}), 404
        cur.execute(
            "UPDATE items SET name=%s, quantity=%s, location=%s WHERE id=%s",
            (clean["name"], clean["quantity"], clean["location"], item_id),
        )
    conn.close()
    return jsonify({"updated": item_id}), 200


@app.delete("/items/<int:item_id>")
def delete_item(item_id):
    conn = get_conn()
    with conn.cursor() as cur:
        cur.execute("DELETE FROM items WHERE id = %s", (item_id,))
        deleted = cur.rowcount
    conn.close()
    if deleted == 0:
        return jsonify({"error": "item tidak ditemukan"}), 404
    return jsonify({"deleted": item_id}), 200


@app.errorhandler(404)
def not_found(_):
    return jsonify({"error": "route tidak ditemukan"}), 404


@app.errorhandler(Exception)
def server_error(exc):
    print(f"ERROR: {exc}")
    return jsonify({"error": "terjadi kesalahan server"}), 500


if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=5000)

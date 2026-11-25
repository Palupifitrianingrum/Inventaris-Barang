"""Bukti koneksi EC2 -> RDS. Jalankan: python3 test_connection.py"""
import os
import sys

import pymysql

try:
    conn = pymysql.connect(
        host=os.environ["DB_HOST"],
        port=int(os.environ.get("DB_PORT", "3306")),
        user=os.environ["DB_USER"],
        password=os.environ["DB_PASSWORD"],
        database=os.environ.get("DB_NAME", "inventory"),
        connect_timeout=5,
    )
except KeyError as exc:
    sys.exit(f"Environment variable belum di-set: {exc}")
except pymysql.MySQLError as exc:
    sys.exit(f"GAGAL konek ke database: {exc}")

with conn.cursor() as cur:
    cur.execute("SELECT VERSION()")
    print("Koneksi BERHASIL. MySQL version:", cur.fetchone()[0])
    cur.execute("SHOW TABLES")
    print("Tabel:", [row[0] for row in cur.fetchall()])
conn.close()

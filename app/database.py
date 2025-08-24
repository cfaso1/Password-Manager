import sqlite3
from app import crypto

DB_FILE = "vault.db"

def init_db(db_folder):
    conn = sqlite3.connect(db_folder / DB_FILE)
    cursor = conn.cursor()
    cursor.execute("""
            CREATE TABLE IF NOT EXISTS vault (
                if INTEGER PRIMARY KEY AUTOINCREMENT,
                website TEXT NOT NULL,
                username TEXT NOT NULL,
                password TEXT NOT NULL
            )
        """)
    conn.commit()
    return conn

def add_entry(conn, website, username, password, key):
    cursor = conn.cursor()
    encrypted_pw = crypto.encrypt(password, key)
    cursor.execute("INSERT INTO vault (website, username, password) VALUES (?, ?, ?)",
                   (website, username, encrypted_pw))
    conn.commit()

def get_entry(conn, website, key):
    cursor = conn.cursor()
    cursor.execute("SELECT website, username, password FROM vault WHERE website = ?", (website,))
    result = cursor.fetchone()
    if result:
        website, username, encrypted_password = result
        decrypted_password = crypto.decrypt(encrypted_password, key)
        return (website, username, decrypted_password)
    else:
        return None, None, None

def update_entry(conn, website, new_username, new_password, key):
    cursor = conn.cursor()
    encrypted_pw = crypto.encrypt(new_password, key)
    cursor.execute("UPDATE vault SET password = ?, username = ? WHERE website = ?",
                   (encrypted_pw, new_username, website))
    conn.commit()

def delete_entry(conn, website):
    cursor = conn.cursor()
    cursor.execute("DELETE FROM vault WHERE website = ?", (website,))
    conn.commit()

def store_check_value(conn, key):
    check = crypto.encrypt("vault_check", key)
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS meta (check_value TEXT)")
    cursor.execute("DELETE FROM meta")
    cursor.execute("INSERT INTO meta VALUES (?)", (check,))
    conn.commit()

def get_all_entries(conn):
    cursor = conn.cursor()
    cursor.execute("SELECT website FROM vault WHERE website IS NOT NULL AND website <> ''ORDER BY LOWER(website)")
    rows = cursor.fetchall()
    return [r[0] for r in rows]
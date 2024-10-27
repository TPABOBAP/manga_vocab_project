import sqlite3

def check_tables():
    conn = sqlite3.connect("manga_vocab.db")
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    conn.close()
    return tables

print(check_tables())

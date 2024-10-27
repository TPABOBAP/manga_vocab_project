import sqlite3
import os

def init_db():
    conn = sqlite3.connect("manga_vocab.db")
    cursor = conn.cursor()
    
    # Создание таблицы известных слов
    cursor.execute(""" 
        CREATE TABLE IF NOT EXISTS known_words (
            word TEXT PRIMARY KEY
        )
    """)

    # Создание таблицы манги с полем для PDF-файла и уникальностью на пару title-chapter
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS manga (
            id INTEGER PRIMARY KEY,
            title TEXT,
            chapter INTEGER,
            text TEXT,
            pdf_filename TEXT UNIQUE,
            UNIQUE(title, chapter)
        )
    """)

    # Создание таблицы словаря
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS vocabulary (
            word TEXT PRIMARY KEY,
            translation TEXT
        )
    """)

    conn.commit()
    conn.close()


if __name__ == "__main__":
    init_db()

from flask import Flask, render_template, request, jsonify
import os
import sqlite3
from manga_processor import extract_text_from_pdf, get_unique_words, translate_words
from db_setup import init_db  # Импортируйте функцию инициализации

app = Flask(__name__)
DATABASE = 'manga_vocab.db'

# Инициализация базы данных
init_db()

def query_db(query, args=(), one=False):
    con = sqlite3.connect(DATABASE)
    cur = con.execute(query, args)
    rv = cur.fetchall()
    con.close()
    return (rv[0] if rv else None) if one else rv

@app.route('/')
def index():
    manga_list = query_db("SELECT title, chapter FROM manga")
    return render_template('index.html', manga_list=manga_list)

@app.route('/upload', methods=['POST'])
def upload_manga():
    file = request.files['file']
    title = request.form['title']
    chapter = int(request.form['chapter'])

    # Создаем директорию uploads, если её нет
    uploads_dir = "uploads"
    if not os.path.exists(uploads_dir):
        os.makedirs(uploads_dir)

    pdf_path = os.path.join(uploads_dir, file.filename)
    file.save(pdf_path)
    
    text = extract_text_from_pdf(pdf_path)
    unique_words = get_unique_words(text)

    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    new_words = []

    # Сначала собираем уникальные слова
    for word in unique_words:
        cursor.execute("SELECT translation FROM vocabulary WHERE word=?", (word,))
        result = cursor.fetchone()
        if result is None:
            new_words.append(word)

    # Переводим новые слова
    translations = translate_words(new_words)
    for word, translation in translations.items():
        word_exists = cursor.execute("SELECT * FROM vocabulary WHERE word = ?", (word,)).fetchone()
        if not word_exists:
            try:
                cursor.execute("INSERT INTO vocabulary (word, translation) VALUES (?, ?)", (word, translation))
                print(f"Added new word: {word} with translation: {translation}")
            except sqlite3.IntegrityError:
                print(f"Integrity error for word '{word}'. It might already exist.")
        else:
            print(f"The word '{word}' already exists in the vocabulary.")

    # Вставляем информацию о манге
    cursor.execute("INSERT INTO manga (title, chapter, text) VALUES (?, ?, ?)", (title, chapter, text))
    conn.commit()
    conn.close()

    return jsonify({"message": "Манга загружена и обработана."})

@app.route('/manga/<title>/<chapter>', methods=['GET'])
def view_manga_words(title, chapter):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    # Получаем текст манги
    cursor.execute("SELECT text FROM manga WHERE title=? AND chapter=?", (title, chapter))
    manga_text = cursor.fetchone()

    if manga_text:
        text = manga_text[0]
        unique_words = get_unique_words(text)
    else:
        unique_words = []

    conn.close()
    return render_template('manga_words.html', title=title, chapter=chapter, unique_words=unique_words)

@app.route('/add_known_word', methods=['POST'])
def add_known_word():
    word = request.form['word']
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    # Здесь вы можете сохранить информацию о знакомых словах
    cursor.execute("INSERT INTO known_words (word) VALUES (?)", (word,))
    conn.commit()
    conn.close()

    return jsonify({"message": f"Слово '{word}' добавлено в знакомые слова."})



if __name__ == "__main__":
    app.run(host="0.0.0.0", port=80)

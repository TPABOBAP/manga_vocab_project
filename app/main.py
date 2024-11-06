from flask import Flask, render_template, request, jsonify, send_from_directory
import os
import sqlite3
from manga_processor import extract_text_from_pdf, get_unique_words, translate_words
from db_setup import init_db  # Импортируйте функцию инициализации
import argostranslate.package
import argostranslate.translate

# Инициализируйте список пакетов при старте приложения
argostranslate.package.update_package_index()
available_packages = argostranslate.package.get_available_packages()
package_to_install = next(filter(lambda x: x.from_code == "en" and x.to_code == "ru", available_packages))
argostranslate.package.install_from_path(package_to_install.download())

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

@app.route('/translate_word', methods=['POST'])
def translate_word():
    word = request.json.get('word')  # Получаем слово из запроса
    if word:
        translated_text = argostranslate.translate.translate(word, "en", "ru")
        return jsonify({"translation": translated_text})
    return jsonify({"error": "Не удалось перевести слово"}), 400

@app.route('/upload', methods=['POST'])
def upload_manga():
    file = request.files['file']
    title = request.form['title']
    chapter = int(request.form['chapter'])

    # Создаем директорию uploads, если её нет
    uploads_dir = "uploads"
    if not os.path.exists(uploads_dir):
        os.makedirs(uploads_dir)

    # Генерация уникального имени файла на основе названия и номера главы
    unique_filename = f"{title}_chapter_{chapter}_{file.filename}"
    pdf_path = os.path.join(uploads_dir, unique_filename)
    file.save(pdf_path)
    
    # Извлекаем текст и обрабатываем слова
    text = extract_text_from_pdf(pdf_path)
    unique_words = get_unique_words(text)

    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    new_words = []

    # Добавление слов в таблицу vocabulary
    for word in unique_words:
        cursor.execute("SELECT translation FROM vocabulary WHERE word=?", (word,))
        result = cursor.fetchone()
        if result is None:
            new_words.append(word)

    # Перевод и добавление новых слов
    translations = translate_words(new_words)
    for word, translation in translations.items():
        word_exists = cursor.execute("SELECT * FROM vocabulary WHERE word = ?", (word,)).fetchone()
        if not word_exists:
            cursor.execute("INSERT INTO vocabulary (word, translation) VALUES (?, ?)", (word, translation))

    # Вставляем информацию о манге в таблицу, включая имя файла
    cursor.execute("INSERT INTO manga (title, chapter, text, pdf_filename) VALUES (?, ?, ?, ?)", 
                   (title, chapter, text, unique_filename))
    conn.commit()
    conn.close()

    return render_template('upload_success.html', title=title)


@app.route('/manga/<title>/<chapter>', methods=['GET'])
def view_manga_words(title, chapter):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    # Получаем текст манги и уникальные слова
    cursor.execute("SELECT text FROM manga WHERE title=? AND chapter=?", (title, chapter))
    manga_text = cursor.fetchone()
    
    # Получаем уникальные слова и известные слова
    if manga_text:
        text = manga_text[0]
        unique_words = get_unique_words(text)
        known_words = set(word[0] for word in cursor.execute("SELECT word FROM known_words").fetchall())
    else:
        unique_words = []
        known_words = set()

    conn.close()
    return render_template('manga_words.html', title=title, chapter=chapter, unique_words=unique_words, known_words=known_words)



@app.route('/add_known_word', methods=['POST'])
def add_known_word():
    word = request.form['word']
    conn = sqlite3.connect(DATABASE)  # Замените на ваше имя базы данных
    cursor = conn.cursor()

    # Проверяем, существует ли слово в базе данных
    cursor.execute("SELECT * FROM known_words WHERE word = ?", (word,))
    existing_word = cursor.fetchone()

    if existing_word:
        # Если слово уже существует, возвращаем ошибку
        return jsonify({"message": f"Слово '{word}' уже было добавлено в словарь."}), 400
    else:
        # Если слово не существует, добавляем его
        cursor.execute("INSERT INTO known_words (word) VALUES (?)", (word,))
        conn.commit()
        return jsonify({"message": f"Слово '{word}' добавлено в словарь выученных слов."}), 200


# Новый маршрут для выбора действий
@app.route('/manga/<title>/<chapter>/options', methods=['GET'])
def manga_options(title, chapter):
    return render_template('manga_options.html', title=title, chapter=chapter)


@app.route('/toggle_known_word', methods=['POST'])
def toggle_known_word():
    word = request.form['word']
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    # Проверяем статус слова
    cursor.execute("SELECT * FROM known_words WHERE word = ?", (word,))
    existing_word = cursor.fetchone()

    if existing_word:
        # Удаляем слово из известных
        cursor.execute("DELETE FROM known_words WHERE word = ?", (word,))
        conn.commit()
        status = False
        message = f"Слово '{word}' удалено из словаря."
    else:
        # Добавляем слово в известные
        cursor.execute("INSERT INTO known_words (word) VALUES (?)", (word,))
        conn.commit()
        status = True
        message = f"Слово '{word}' добавлено в словарь выученных слов."

    conn.close()
    return jsonify({"status": status, "message": message})


@app.route('/download/<string:manga_title>/<int:chapter_number>', methods=['GET'])
def download_pdf(manga_title, chapter_number):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    # Получаем pdf_filename из базы данных по названию манги и номеру главы
    cursor.execute("SELECT pdf_filename FROM manga WHERE title=? AND chapter=?", (manga_title, chapter_number))
    pdf_filename = cursor.fetchone()

    if pdf_filename is None:
        return "File not found", 404

    # Проверяем, существует ли файл
    pdf_path = os.path.join('uploads', pdf_filename[0])
    if not os.path.exists(pdf_path):
        return "File not found", 404

    return send_from_directory(directory='uploads', path=pdf_filename[0], as_attachment=True)

    

@app.route('/manga/<title>/<chapter>/unknown_words', methods=['GET'])
def view_unknown_words(title, chapter):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    # Получаем текст манги
    cursor.execute("SELECT text FROM manga WHERE title=? AND chapter=?", (title, chapter))
    manga_text = cursor.fetchone()

    # Получаем только неизвестные слова
    if manga_text:
        text = manga_text[0]
        unique_words = get_unique_words(text)
        known_words = set(word[0] for word in cursor.execute("SELECT word FROM known_words").fetchall())
        unknown_words = [word for word in unique_words if word not in known_words]
    else:
        unknown_words = []

    conn.close()
    return render_template('unknown_words.html', title=title, chapter=chapter, unknown_words=unknown_words)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=80)

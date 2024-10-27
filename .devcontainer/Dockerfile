# Используем базовый образ Python
FROM python:3.9-slim

# Устанавливаем необходимые пакеты
RUN apt-get update && \
    apt-get install -y tesseract-ocr libgl1 && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем файл с зависимостями
COPY app/requirements.txt /app/

# Устанавливаем зависимости
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Скачиваем необходимые данные NLTK
RUN python -m nltk.downloader punkt stopwords
RUN python -m nltk.downloader punkt punkt_tab stopwords

# Копируем остальной код приложения
COPY app /app

# Указываем порт для приложения
EXPOSE 80

# Запускаем приложение Flask
CMD ["flask", "--app", "main.py", "--debug", "run", "--host=0.0.0.0", "--port=80"]

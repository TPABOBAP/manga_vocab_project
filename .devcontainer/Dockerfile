# Используем базовый образ Python
FROM python:3.9-slim

# Устанавливаем необходимые пакеты
RUN apt-get update && \
    apt-get install -y tesseract-ocr libgl1 && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*  # Удаляем кэш, чтобы уменьшить размер образа

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем файл с зависимостями
COPY app/requirements.txt /app/

# Устанавливаем зависимости
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt


RUN python -m nltk.downloader punkt stopwords
RUN python -m nltk.downloader punkt punkt_tab stopwords


COPY app /app

# Запускаем инициализацию базы данных
RUN python db_setup.py

# Указываем порт для приложения
EXPOSE 80

# Указываем команду для запуска приложения
CMD ["python", "main.py"]

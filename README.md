# Manga Vocabulary Project

This project allows you to upload a PDF of a manga chapter, extract words, translate them, and interact with the vocabulary through a web interface. The website provides a user-friendly way to learn new words by clicking and marking words that you've learned.

## How to Run on Google Colab

1. Run this code block:

```bash
!git clone https://github.com/TPABOBAP/manga_vocab_project
!pip install -r /content/manga_vocab_project/app/requirements.txt
from google.colab.output import eval_js
url = eval_js("google.colab.kernel.proxyPort(5000)")
print('Open the link to use your web interface! -> ', url)
!python /content/manga_vocab_project/app/main.py
```

2. **Open the Web Interface**  
   After running the command to start the Flask app, Colab will provide a link to access the web interface.  
   Click on the link printed by the `eval_js` command to open the web app in your browser.

## How the Website Works

The website offers several features to interact with vocabulary extracted from manga chapters:

1. **Upload PDF File**  
   Upload a PDF of a manga chapter by clicking the "Upload" button.  
   Enter the chapter title and chapter number.  
   Wait for the system to process and extract the text from the PDF.

2. **Translation Feature**  
   Single-click on any word to get its translation from English to Russian.  
   Double-click on a word to see example sentences with translations for that word.

3. **Vocabulary Learning**  
   You can mark words as learned by checking a box next to the word. This helps you keep track of the words you have already learned.

4. **Interactive Vocabulary List**  
   After the PDF is uploaded and processed, the extracted vocabulary will be displayed on the web interface.  
   You can interact with the list, translating words, and marking words that you have already learned.

## Technologies Used

- **Flask**: Web framework for serving the app.
- **PyMuPDF**: Used to extract text from the uploaded PDF files.
- **NLTK**: Natural language processing for tokenizing and processing words.
- **Argos Translate**: Translation API for translating words (English to Russian).
- **SQLite**: Database to store manga details and vocabulary.
- **HTML, CSS**: Front-end structure and styling.

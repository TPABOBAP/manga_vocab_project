import fitz
import pytesseract
from PIL import Image
import nltk
from nltk.corpus import stopwords

nltk.download("stopwords")
stop_words = set(stopwords.words("english"))

def extract_text_from_pdf(pdf_path):
    text = ""
    doc = fitz.open(pdf_path)
    for page_num in range(doc.page_count):
        page = doc.load_page(page_num)
        pix = page.get_pixmap()
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        page_text = pytesseract.image_to_string(img, lang='eng')
        text += page_text + "\n"
    doc.close()
    return text

def get_unique_words(text):
    words = nltk.word_tokenize(text)
    words = [word.lower() for word in words if word.isalpha() and word.lower() not in stop_words]
    unique_words = list(set(words))
    return unique_words

def translate_words(words):
    translator = Translator()
    translations = {}
    for word in words:
        translated = translator.translate(word, src='en', dest='ru')
        translations[word] = translated.text
    return translations

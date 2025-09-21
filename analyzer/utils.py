import os
from docx import Document
import PyPDF2
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile

def extract_text_from_file(file_path):
    """Estrae testo da PDF o DOCX"""
    
    _, file_extension = os.path.splitext(file_path.lower())
    
    try:
        if file_extension == '.pdf':
            return extract_text_from_pdf(file_path)
        elif file_extension == '.docx':
            return extract_text_from_docx(file_path)
        else:
            raise ValueError(f"Formato file non supportato: {file_extension}")
    except Exception as e:
        raise Exception(f"Errore nell'estrazione del testo: {str(e)}")

def extract_text_from_pdf(file_path):
    """Estrae testo da file PDF"""
    text = ""
    
    with open(file_path, 'rb') as file:
        pdf_reader = PyPDF2.PdfReader(file)
        
        for page_num in range(len(pdf_reader.pages)):
            page = pdf_reader.pages[page_num]
            text += page.extract_text()
    
    return text

def extract_text_from_docx(file_path):
    """Estrae testo da file DOCX"""
    doc = Document(file_path)
    text = ""
    
    for paragraph in doc.paragraphs:
        text += paragraph.text + "\n"
    
    return text

def clean_text(text):
    """Pulisce e normalizza il testo estratto"""
    # Rimuove caratteri speciali e normalizza spazi
    import re
    
    # Rimuove caratteri di controllo
    text = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', text)
    
    # Normalizza spazi multipli
    text = re.sub(r'\s+', ' ', text)
    
    # Rimuove spazi all'inizio e alla fine
    text = text.strip()
    
    return text
import os
import logging
import subprocess
import tempfile
from typing import Optional

logger = logging.getLogger(__name__)

def extract_text_from_file(file_path: str, file_type: Optional[str] = None) -> str:
    """
    Извлекает текст из файла резюме. 
    Поддерживает форматы PDF, DOC и DOCX.
    """
    if not file_path or not os.path.exists(file_path):
        logger.error(f"Файл не существует: {file_path}")
        return ""
    
    # Если тип файла не указан, определяем его по расширению
    if not file_type:
        _, extension = os.path.splitext(file_path)
        file_type = extension[1:].lower()  # удаляем точку
    
    try:
        if file_type == 'pdf':
            return extract_text_from_pdf(file_path)
        elif file_type in ['doc', 'docx']:
            return extract_text_from_doc(file_path, file_type)
        else:
            logger.error(f"Неподдерживаемый тип файла: {file_type}")
            return ""
    except Exception as e:
        logger.error(f"Ошибка при извлечении текста из файла {file_path}: {str(e)}")
        return ""

def extract_text_from_pdf(file_path: str) -> str:
    """Извлекает текст из PDF файла."""
    try:
        # Проверяем наличие pdftotext
        import subprocess
        
        # Создаем временный файл для вывода текста
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            temp_path = temp_file.name
        
        # Вызываем pdftotext
        result = subprocess.run(
            ['pdftotext', '-layout', '-enc', 'UTF-8', file_path, temp_path],
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0:
            logger.error(f"Ошибка при выполнении pdftotext: {result.stderr}")
            return ""
        
        # Читаем извлеченный текст
        with open(temp_path, 'r', encoding='utf-8') as f:
            text = f.read()
        
        # Удаляем временный файл
        os.unlink(temp_path)
        
        return text
    except FileNotFoundError:
        logger.error("pdftotext не найден. Установите poppler-utils: sudo apt-get install poppler-utils")
        return ""
    except Exception as e:
        logger.error(f"Ошибка при извлечении текста из PDF: {str(e)}")
        return ""

def extract_text_from_doc(file_path: str, file_type: str) -> str:
    """Извлекает текст из DOC или DOCX файла."""
    try:
        if file_type == 'docx':
            # Для DOCX используем python-docx
            from docx import Document
            doc = Document(file_path)
            return '\n'.join([para.text for para in doc.paragraphs])
        elif file_type == 'doc':
            # Для DOC используем antiword
            result = subprocess.run(
                ['antiword', file_path],
                capture_output=True,
                text=True
            )
            
            if result.returncode != 0:
                logger.error(f"Ошибка при выполнении antiword: {result.stderr}")
                return ""
                
            return result.stdout
    except ImportError:
        logger.error("Необходимые библиотеки не установлены. Установите python-docx для DOCX или antiword для DOC.")
        return ""
    except Exception as e:
        logger.error(f"Ошибка при извлечении текста из {file_type.upper()}: {str(e)}")
        return ""
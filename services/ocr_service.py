import pytesseract
from PIL import Image
import os

# Tesseract install කළ තැන (Windows සඳහා පමණයි)
# ඔබේ පරිගණකයේ Tesseract ඇති තැන මෙතැනට දෙන්න.
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

class OCRService:
    @staticmethod
    def extract_text_from_image(image_file):

        try:
            img = Image.open(image_file)
            
            extracted_text = pytesseract.image_to_string(img, lang='eng')
            
            return extracted_text.strip()
        except Exception as e:
            print(f"❌ OCR Error: {e}")
            return ""
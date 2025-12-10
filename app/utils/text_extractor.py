import os
import json
import pdfplumber
import pytesseract
from PIL import Image
# import fitz  # PyMuPDF -- REMOVED
from typing import List, Dict, Any

# Ensure pytesseract path is set if needed, or assume it's in PATH
# pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe' 


def extract_text_from_pdf(file_path: str) -> List[Dict[str, Any]]:
    """
    Extracts text from a PDF file using both digital text extraction (pdfplumber)
    and OCR (Tesseract) for images/scanned pages.
    """
    print(f"Starting extraction for: {file_path}")
    text_blocks = []
    
    # Check for associated cell info (from Excel conversion)
    cell_info_path = file_path.rsplit('.', 1)[0] + '_cellinfo.json'
    cell_info = None
    if os.path.exists(cell_info_path):
        try:
            with open(cell_info_path, 'r', encoding='utf-8') as f:
                cell_info = json.load(f)
        except Exception as e:
            print(f"Error loading cell info: {e}")

    try:
        with pdfplumber.open(file_path) as pdf:
            for page_num, page in enumerate(pdf.pages):
                current_page = page_num + 1
                
                # 1. Extract digital text
                try:
                    text = page.extract_text()
                    if text:
                        paragraphs = text.split('\n')
                        for i, paragraph in enumerate(paragraphs):
                            if paragraph.strip():
                                block = {
                                    "text": paragraph,
                                    "page": current_page,
                                    "source": "text",
                                    "metadata": {}
                                }
                                # Try to map to Excel info
                                if cell_info and i < len(cell_info):
                                    block["metadata"]["row"] = cell_info[i].get("row")
                                    block["metadata"]["col"] = cell_info[i].get("col")
                                
                                text_blocks.append(block)
                except Exception as e:
                    print(f"Error executing pdfplumber on page {current_page}: {e}")

                # 3. OCR on page image (Fallback/Enrichment)
                # We perform OCR if digital text is sparse or just to be safe
                try:
                    # Use pdfplumber's to_image (requires Pillow/Wand/etc)
                    # pdfplumber to_image returns a PageImage object, .original is the PIL Image
                    page_image = page.to_image(resolution=200)
                    pil_img = page_image.original
                    
                    # Run OCR using Tesseract
                    ocr_text = pytesseract.image_to_string(pil_img)
                    
                    # Add unique OCR text
                    if ocr_text.strip():
                        # Simple de-duplication
                        is_duplicate = False
                        for block in text_blocks:
                            if block['page'] == current_page and ocr_text.strip() in block['text']:
                                is_duplicate = True
                                break
                        
                        if not is_duplicate:
                            text_blocks.append({
                                "text": ocr_text.strip(),
                                "page": current_page,
                                "source": "ocr_tesseract",
                                "metadata": {}
                            })
                            
                except Exception as e:
                    print(f"Error executing OCR on page {current_page}: {e}")

    except Exception as e:
        print(f"Fatal error reading PDF {file_path}: {e}")
        return []

    return text_blocks

def save_extracted_text(file_path: str, text_blocks: List[Dict[str, Any]]):
    """Saves extracted text blocks to a JSON file."""
    json_path = file_path + "_extracted.json"
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(text_blocks, f, ensure_ascii=False, indent=2)
    return json_path

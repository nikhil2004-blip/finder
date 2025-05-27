import json
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import pdfplumber
import os
from paddleocr import PaddleOCR
from PIL import Image as PILImage
import io
import re
import difflib

UPLOAD_DIR = "uploads"

router = APIRouter()

# Initialize PaddleOCR for both English and Chinese
paddle_ocr_en = PaddleOCR(use_angle_cls=True, lang='en')
paddle_ocr_zh = PaddleOCR(use_angle_cls=True, lang='ch')

class SearchQuery(BaseModel):
    query: str
    max_results: int = 10

class SearchResult(BaseModel):
    text: str
    file_name: str
    page_number: int
    row: Optional[int] = None
    col: Optional[int] = None
    source: Optional[str] = None

# Helper: Extract all text (including OCR from images) from PDF and Excel
# For Excel, include ocr_text from cellinfo JSON

def extract_text_from_pdf(file_path: str) -> List[dict]:
    text_blocks = []
    cell_info_path = file_path.rsplit('.', 1)[0] + '_cellinfo.json'
    cell_info = None
    if os.path.exists(cell_info_path):
        with open(cell_info_path, 'r', encoding='utf-8') as f:
            cell_info = json.load(f)
    with pdfplumber.open(file_path) as pdf:
        for page_num, page in enumerate(pdf.pages):
            # 1. Extract digital text
            try:
                text = page.extract_text()
            except Exception as e:
                print(f"[ERROR] extract_text failed on page {page_num+1} of {file_path}: {e}")
                text = None
            if text:
                for i, paragraph in enumerate(text.split('\n')):
                    block = {
                        "text": paragraph,
                        "page": page_num + 1,
                        "source": "text"
                    }
                    if cell_info and i < len(cell_info):
                        block["row"] = cell_info[i].get("row")
                        block["col"] = cell_info[i].get("col")
                        # Add OCR text from Excel cell if present
                        if cell_info[i].get("ocr_text"):
                            for ocr_text in cell_info[i]["ocr_text"]:
                                text_blocks.append({
                                    "text": ocr_text,
                                    "page": page_num + 1,
                                    "row": cell_info[i].get("row"),
                                    "col": cell_info[i].get("col"),
                                    "source": "excel_ocr"
                                })
                    text_blocks.append(block)
            # 2. OCR on page image (for PDFs)
            try:
                pil_img = page.to_image(resolution=300).original
                try:
                    ocr_results_en = paddle_ocr_en.ocr(pil_img)
                except Exception as e:
                    print(f"[ERROR] PaddleOCR EN failed on page {page_num+1} of {file_path}: {e}")
                    ocr_results_en = None
                try:
                    ocr_results_zh = paddle_ocr_zh.ocr(pil_img)
                except Exception as e:
                    print(f"[ERROR] PaddleOCR ZH failed on page {page_num+1} of {file_path}: {e}")
                    ocr_results_zh = None
                ocr_texts = set()
                for result in (ocr_results_en[0] if ocr_results_en and len(ocr_results_en) > 0 else []):
                    ocr_texts.add(result[1][0])
                for result in (ocr_results_zh[0] if ocr_results_zh and len(ocr_results_zh) > 0 else []):
                    ocr_texts.add(result[1][0])
                for ocr_text in ocr_texts:
                    if ocr_text.strip():
                        text_blocks.append({
                            "text": ocr_text,
                            "page": page_num + 1,
                            "source": "ocr"
                        })
            except Exception as e:
                print(f"[ERROR] to_image or OCR failed on page {page_num+1} of {file_path}: {e}")
    # Log extracted text blocks for debugging
    print(f"Extracted from {file_path}:")
    for block in text_blocks:
        print(f"Page {block.get('page')}: {block.get('text')}")
    return text_blocks

def is_chinese_subsequence(query, text):
    # Returns True if all characters in query appear in order in text
    it = iter(text)
    return all(char in it for char in query)

def chinese_char_overlap(query, text, threshold=0.6):
    query_chars = set(query)
    if not query_chars:
        return False
    overlap = sum(1 for c in query_chars if c in text)
    return (overlap / len(query_chars)) >= threshold

@router.post("")
async def normal_search(query: SearchQuery) -> List[SearchResult]:
    """
    Robust keyword search: supports English (split by spaces, match any word) and Chinese (character overlap match for fuzzy/partial search)
    """
    try:
        results = []
        def contains_chinese(text):
            return re.search(r"[\u4e00-\u9fff]", text) is not None

        is_chinese = contains_chinese(query.query)
        for filename in os.listdir(UPLOAD_DIR):
            if filename.endswith('.pdf'):
                file_path = os.path.join(UPLOAD_DIR, filename)
                text_blocks = extract_text_from_pdf(file_path)
                for block in text_blocks:
                    text = block["text"]
                    text_lower = text.lower()
                    if is_chinese:
                        if chinese_char_overlap(query.query, text):
                            results.append(SearchResult(
                                text=block["text"],
                                file_name=filename,
                                page_number=block["page"],
                                row=block.get("row"),
                                col=block.get("col"),
                                source=block.get("source")
                            ))
                    else:
                        # For English, match if ANY query word is a substring (case-insensitive)
                        query_terms = [term.lower() for term in query.query.split()]
                        if any(term in text_lower for term in query_terms):
                            results.append(SearchResult(
                                text=block["text"],
                                file_name=filename,
                                page_number=block["page"],
                                row=block.get("row"),
                                col=block.get("col"),
                                source=block.get("source")
                            ))
        return results[:query.max_results]
    except Exception as e:
        import traceback
        print("Search failed:", e)
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}") 
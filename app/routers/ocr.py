from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
import pytesseract
from paddleocr import PaddleOCR
import fitz  # PyMuPDF
from PIL import Image
import io
import os
from typing import List, Dict

router = APIRouter()

# Initialize PaddleOCR for both English and Chinese
paddle_ocr_en = PaddleOCR(use_angle_cls=True, lang='en')
paddle_ocr_zh = PaddleOCR(use_angle_cls=True, lang='ch')

@router.post("/extract")
async def extract_text_from_image(
    file: UploadFile = File(...),
    language: str = "auto"
):
    """
    Extract text from image using OCR (auto-detect English/Chinese)
    """
    try:
        contents = await file.read()
        image = Image.open(io.BytesIO(contents))
        detected_language = "English"
        text = ""

        if language == "auto":
            # Try both PaddleOCR models and pick the one with more text
            result_en = paddle_ocr_en.ocr(image)
            text_en = " ".join([line[1][0] for line in result_en[0]]) if result_en and result_en[0] else ""
            result_zh = paddle_ocr_zh.ocr(image)
            text_zh = " ".join([line[1][0] for line in result_zh[0]]) if result_zh and result_zh[0] else ""
            # Choose the language with more extracted text
            if len(text_zh) > len(text_en):
                text = text_zh
                detected_language = "Chinese"
            else:
                text = text_en
                detected_language = "English"
        elif language == "en":
            result_en = paddle_ocr_en.ocr(image)
            text = " ".join([line[1][0] for line in result_en[0]]) if result_en and result_en[0] else ""
            detected_language = "English"
        elif language == "zh":
            result_zh = paddle_ocr_zh.ocr(image)
            text = " ".join([line[1][0] for line in result_zh[0]]) if result_zh and result_zh[0] else ""
            detected_language = "Chinese"
        else:
            raise HTTPException(status_code=400, detail="Unsupported language")

        return {
            "text": text,
            "detected_language": detected_language,
            "message": f"Text extracted using {detected_language} OCR."
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"OCR extraction failed: {str(e)}")

@router.post("/extract-pdf")
async def extract_text_from_pdf(
    file: UploadFile = File(...),
    language: str = "eng"
):
    """
    Extract text from PDF using OCR
    """
    try:
        # Read PDF file
        contents = await file.read()
        pdf_document = fitz.open(stream=contents, filetype="pdf")
        
        extracted_text = []
        
        # Process each page
        for page_num in range(len(pdf_document)):
            page = pdf_document[page_num]
            
            # Convert page to image
            pix = page.get_pixmap()
            img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
            
            # Extract text based on language
            if language == "eng":
                text = pytesseract.image_to_string(img)
            elif language == "chi":
                result = paddle_ocr_zh.ocr(img)
                text = " ".join([line[1][0] for line in result[0]])
            else:
                raise HTTPException(status_code=400, detail="Unsupported language")
            
            extracted_text.append({
                "page": page_num + 1,
                "text": text
            })
        
        return {
            "pages": extracted_text,
            "language": language
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 
from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
import pytesseract
# import fitz  # PyMuPDF -- REMOVED
import pdfplumber
from PIL import Image
import io
import os
from typing import List, Dict

router = APIRouter()

@router.post("/extract")
async def extract_text_from_image(
    file: UploadFile = File(...),
    language: str = "eng"
):
    """
    Extract text from image using Tesseract OCR
    """
    try:
        contents = await file.read()
        image = Image.open(io.BytesIO(contents))
        
        # Tesseract execution
        text = pytesseract.image_to_string(image, lang='eng')  # Default to english for stability
        
        return {
            "text": text,
            "detected_language": "English (Tesseract)",
            "message": "Text extracted using Tesseract."
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"OCR extraction failed: {str(e)}")

@router.post("/extract-pdf")
async def extract_text_from_pdf(
    file: UploadFile = File(...),
    language: str = "eng"
):
    """
    Extract text from PDF using OCR (Tesseract + pdfplumber for image ref)
    """
    try:
        # Save temp file because pdfplumber needs path or file object
        contents = await file.read()
        
        extracted_text = []

        with pdfplumber.open(io.BytesIO(contents)) as pdf:
            for page_num, page in enumerate(pdf.pages):
                # Convert page to image for OCR
                pil_img = page.to_image(resolution=200).original
                
                # Extract text using Tesseract
                text = pytesseract.image_to_string(pil_img)
                
                extracted_text.append({
                    "page": page_num + 1,
                    "text": text
                })
        
        return {
            "pages": extracted_text,
            "language": "eng"
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
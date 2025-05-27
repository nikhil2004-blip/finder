from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse, FileResponse
import os
import pandas as pd
import fitz  # PyMuPDF
from ..utils.file_converter import convert_excel_to_pdf
from ..utils.file_storage import save_upload_file

router = APIRouter()

UPLOAD_DIR = "uploads"
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)

@router.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    """
    Upload a PDF or Excel file
    """
    try:
        # Validate file type
        if not file.filename.endswith(('.pdf', '.xlsx', '.xls')):
            raise HTTPException(status_code=400, detail="Only PDF and Excel files are allowed")

        # Save the uploaded file
        file_path = await save_upload_file(file, UPLOAD_DIR)

        # If Excel file, convert to PDF and extract cell info
        if file.filename.endswith(('.xlsx', '.xls')):
            pdf_path, cell_info_path = await convert_excel_to_pdf(file_path)
            return {
                "message": "File uploaded and converted successfully",
                "original_file": file_path,
                "converted_file": pdf_path,
                "cell_info": cell_info_path
            }

        return {
            "message": "File uploaded successfully",
            "file_path": file_path
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/list")
async def list_files():
    """
    List all uploaded files
    """
    try:
        files = []
        for filename in os.listdir(UPLOAD_DIR):
            if filename.endswith(('.pdf', '.xlsx', '.xls')):
                file_path = os.path.join(UPLOAD_DIR, filename)
                files.append({
                    "filename": filename,
                    "size": os.path.getsize(file_path),
                    "type": "pdf" if filename.endswith('.pdf') else "excel"
                })
        return files
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{filename}")
async def delete_file(filename: str):
    """
    Delete a specific file
    """
    try:
        file_path = os.path.join(UPLOAD_DIR, filename)
        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail="File not found")
        
        os.remove(file_path)
        return {"message": f"File {filename} deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/download/{filename}")
async def download_file(filename: str):
    file_path = os.path.join(UPLOAD_DIR, filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(file_path, filename=filename) 
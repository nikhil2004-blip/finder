from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse, FileResponse
import os
import pandas as pd
from ..utils.file_storage import save_upload_file

router = APIRouter()

UPLOAD_DIR = "uploads"
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)

@router.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    """
    Upload a PDF or Excel file and extract its text immediately.
    """
    try:
        # Validate file type
        if not file.filename.endswith(('.pdf', '.xlsx', '.xls')):
            raise HTTPException(status_code=400, detail="Only PDF and Excel files are allowed")

        # Save the uploaded file
        file_path = await save_upload_file(file, UPLOAD_DIR)

        extraction_source = file_path
        
        from ..utils.text_extractor import extract_text_from_pdf, save_extracted_text
        
        if file_path.endswith('.pdf'):
            text_blocks = extract_text_from_pdf(extraction_source)
            json_path = save_extracted_text(extraction_source, text_blocks)
            blocks_count = len(text_blocks)
        else:
            text_blocks = []
            json_path = ""
            blocks_count = 0

        return {
            "message": "File uploaded and processed successfully",
            "file_path": file_path,
            "processed_json": json_path,
            "blocks_count": blocks_count
        }

    except Exception as e:
        import traceback
        traceback.print_exc()
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
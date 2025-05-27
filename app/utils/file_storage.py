import os
import shutil
from fastapi import UploadFile
from typing import Optional

async def save_upload_file(upload_file: UploadFile, destination: str) -> str:
    """
    Save an uploaded file to the specified destination
    """
    try:
        # Create destination directory if it doesn't exist
        os.makedirs(destination, exist_ok=True)

        # Create file path
        file_path = os.path.join(destination, upload_file.filename)

        # Save the file
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(upload_file.file, buffer)

        return file_path

    except Exception as e:
        raise Exception(f"Error saving file: {str(e)}")

    finally:
        upload_file.file.close()

def get_file_extension(filename: str) -> Optional[str]:
    """
    Get file extension from filename
    """
    try:
        return filename.rsplit('.', 1)[1].lower()
    except:
        return None

def is_valid_file_type(filename: str, allowed_extensions: list) -> bool:
    """
    Check if file type is allowed
    """
    ext = get_file_extension(filename)
    return ext in allowed_extensions if ext else False 
import shutil
import os
from fastapi import UploadFile

UPLOAD_DIR = "static"

def save_upload_file(upload_file: UploadFile, destination_path: str) -> str:
    try:
        os.makedirs(UPLOAD_DIR, exist_ok=True)
        file_path = os.path.join(UPLOAD_DIR, destination_path)
        
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(upload_file.file, buffer)
            
        # Return localhost URL
        return f"http://localhost:8000/static/{destination_path}"
    finally:
        upload_file.file.close()

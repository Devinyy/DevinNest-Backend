from fastapi import APIRouter, UploadFile, File, Request
from app.backstage.schemas import UploadResponse, ApiResponse
import shutil
import os
import uuid
import re
from pathlib import Path

router = APIRouter()

# Define upload directory
UPLOAD_DIR = Path("static/uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

@router.post("/upload", response_model=ApiResponse[UploadResponse], summary="文件上传")
async def upload_file(request: Request, file: UploadFile = File(...)):
    """
    上传文件到服务器。
    """
    # Sanitize and use original filename
    original_filename = file.filename
    # Remove directory paths if present and sanitize characters
    filename = os.path.basename(original_filename)
    filename = re.sub(r'[\\/*?:"<>|]', '_', filename)
    
    # Handle duplicates
    name, ext = os.path.splitext(filename)
    counter = 1
    final_filename = filename
    
    while (UPLOAD_DIR / final_filename).exists():
        final_filename = f"{name}_{counter}{ext}"
        counter += 1
        
    file_path = UPLOAD_DIR / final_filename
    
    # Save file
    with file_path.open("wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    # Construct URL
    # Assuming the app is served at root, and static files are mounted at /static
    base_url = str(request.base_url).rstrip("/")
    file_url = f"{base_url}/static/uploads/{final_filename}"
    
    return ApiResponse(data=UploadResponse(
        url=file_url,
        filename=final_filename,
        path=str(file_path)
    ))

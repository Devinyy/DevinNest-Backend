from fastapi import APIRouter, UploadFile, File, Request
from app.backstage.schemas import UploadResponse, ApiResponse
import shutil
import os
import uuid
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
    # Generate unique filename
    file_ext = os.path.splitext(file.filename)[1]
    unique_filename = f"{uuid.uuid4()}{file_ext}"
    file_path = UPLOAD_DIR / unique_filename
    
    # Save file
    with file_path.open("wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    # Construct URL
    # Assuming the app is served at root, and static files are mounted at /static
    base_url = str(request.base_url).rstrip("/")
    file_url = f"{base_url}/static/uploads/{unique_filename}"
    
    return ApiResponse(data=UploadResponse(
        url=file_url,
        filename=unique_filename
    ))

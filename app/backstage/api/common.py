from fastapi import APIRouter, UploadFile, File, Request
from app.backstage.schemas import UploadResponse, ApiResponse
from app.core.config import settings
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
    # 优先使用配置的对外地址（含端口，如 https://devinnest-api.top:8443），
    # 避免反向代理/Cloudflare 丢失端口导致返回的 URL 不可访问；
    # 未配置 PUBLIC_BASE_URL 时回退到 request.base_url（本地开发）
    base_url = (settings.PUBLIC_BASE_URL or str(request.base_url)).rstrip("/")
    file_url = f"{base_url}/static/uploads/{final_filename}"
    
    return ApiResponse(data=UploadResponse(
        url=file_url,
        filename=final_filename,
        path=str(file_path)
    ))

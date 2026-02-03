from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from app.backstage.schemas import LoginRequest, LoginResponse, UserInfo, ApiResponse
from app.core.database import get_db
from app.models import User
from app.core.security import get_public_key, decrypt_password
from passlib.context import CryptContext

router = APIRouter()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

@router.get("/public-key", response_model=ApiResponse[dict], summary="获取RSA公钥")
async def get_rsa_public_key():
    """
    获取RSA公钥，用于前端登录时加密密码。
    """
    return ApiResponse(data={"publicKey": get_public_key()})

@router.post("/login", response_model=ApiResponse[LoginResponse], summary="用户登录")
async def login(request: LoginRequest, db: Session = Depends(get_db)):
    """
    用户名密码登录，获取 Token。
    密码应使用公钥加密（可选，支持明文兼容）。
    """
    user = db.query(User).filter(User.username == request.username).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    
    # Try to decrypt password
    password = decrypt_password(request.password)
    
    if not pwd_context.verify(password, user.password_hash):
        raise HTTPException(status_code=401, detail="Password not match")

    # Generate a fake token (In production, use JWT with expiration)
    token = f"eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.user_{user.id}"
    
    user_info = UserInfo(
        id=user.id,
        username=user.username,
        avatar=user.avatar or ""
    )
    
    return ApiResponse(data=LoginResponse(token=token, userInfo=user_info))

@router.get("/me", response_model=ApiResponse[UserInfo], summary="获取当前用户信息")
async def get_current_user_info(db: Session = Depends(get_db)):
    """
    校验 Token 有效性并获取用户信息。
    In a real app, you would decode the token to get the user ID.
    """
    # Hardcoded to return the Devin user for now as we don't have full JWT Middleware yet
    user = db.query(User).filter(User.username == "admin").first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
        
    return ApiResponse(data=UserInfo(
        id=user.id,
        username=user.username,
        avatar=user.avatar or ""
    ))

@router.post("/logout", response_model=ApiResponse[dict], summary="退出登录")
async def logout():
    """
    退出登录 (Client side clears token).
    """
    return ApiResponse(message="Logged out successfully")

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from app.core.config import settings
from app.router import api_router
from app.core.database import engine, Base
from app.models import User # Import models to ensure they are registered
from passlib.context import CryptContext
from sqlalchemy.orm import Session
import os
from app.backstage.schemas import ApiResponse

# Create Tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "code": exc.status_code,
            "message": exc.detail,
            "data": None
        },
    )

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=422,
        content={
            "code": 422,
            "message": "Validation Error",
            "data": exc.errors()
        },
    )

# Set all CORS enabled origins
if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# Mount static files
os.makedirs("static/uploads", exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(api_router, prefix=settings.API_V1_STR)

@app.get("/", response_model=ApiResponse[dict])
async def root():
    return ApiResponse(data={"message": "Welcome to DevinNest AI Backend", "docs": "/docs"})

# Initialize default user if not exists (Optional, but helpful for testing)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def init_db():
    from app.core.database import SessionLocal
    db = SessionLocal()
    
    # Check if target user exists
    target_user = db.query(User).filter(User.username == "admin").first()
    
    if not target_user:
        # Check if old admin exists and rename
        old_admin = db.query(User).filter(User.username == "admin").first()
        if old_admin:
            old_admin.username = "admin"
            old_admin.password_hash = pwd_context.hash("admin")
            old_admin.avatar = "/static/avator.png"
            db.add(old_admin)
            print("Renamed admin to admin")
        else:
            # Create new user
            hashed_password = pwd_context.hash("admin")
            user = User(username="admin", password_hash=hashed_password, avatar="/static/avator.png")
            db.add(user)
            print("Created user admin")
        db.commit()
    else:
        # Ensure password is correct
        target_user.password_hash = pwd_context.hash("admin")
        db.add(target_user)
        db.commit()
        print("Updated user admin password")
    
    db.close()

init_db()

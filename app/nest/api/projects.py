from fastapi import APIRouter, Depends
from typing import List
from app.nest.schemas import Project
from app.backstage.schemas import ApiResponse

router = APIRouter()

# Mock Database
fake_projects_db = [
    {"id": 1, "name": "DevinNest Frontend", "description": "The main web application", "owner": "user@example.com"},
    {"id": 2, "name": "AI Agent Service", "description": "Backend service for AI agents", "owner": "user@example.com"},
]

@router.get("/", response_model=ApiResponse[List[Project]])
async def read_projects(skip: int = 0, limit: int = 10):
    """
    Retrieve projects for the current user (DevinNest Web).
    """
    return ApiResponse(data=fake_projects_db[skip : skip + limit])

@router.post("/", response_model=ApiResponse[Project])
async def create_project(project: Project):
    """
    Create a new project.
    """
    fake_projects_db.append(project.dict())
    return ApiResponse(data=project)

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.backstage.schemas import DashboardStats, ApiResponse
from app.core.database import get_db
from app.models import Blog, Snippet, Category, Tag
from datetime import datetime, date

router = APIRouter()

@router.get("/stats", response_model=ApiResponse[DashboardStats], summary="获取统计数据")
async def get_dashboard_stats(db: Session = Depends(get_db)):
    """
    获取首页所需的各项统计指标。
    """
    # Calculate date range for "this month"
    today = date.today()
    first_day_of_month = datetime(today.year, today.month, 1)

    blogs_count = db.query(Blog).count()
    snippets_count = db.query(Snippet).count()
    categories_count = db.query(Category).count()
    tags_count = db.query(Tag).count()
    
    blogs_new_this_month = db.query(Blog).filter(Blog.created_at >= first_day_of_month).count()
    snippets_new_this_month = db.query(Snippet).filter(Snippet.created_at >= first_day_of_month).count()
    
    return ApiResponse(data=DashboardStats(
        blogsCount=blogs_count,
        snippetsCount=snippets_count,
        categoriesCount=categories_count,
        tagsCount=tags_count,
        blogsNewThisMonth=blogs_new_this_month,
        snippetsNewThisMonth=snippets_new_this_month,
        latestActivity=[]
    ))

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import desc
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
    
    # Get latest 5 blogs
    latest_blogs = db.query(Blog).order_by(desc(Blog.created_at)).limit(5).all()
    
    # Get latest 5 snippets
    latest_snippets = db.query(Snippet).order_by(desc(Snippet.created_at)).limit(5).all()
    
    activity_list = []
    
    for b in latest_blogs:
        activity_list.append({
            "id": b.id,
            "title": b.title,
            "type": "blog",
            "createdAt": b.created_at
        })
        
    for s in latest_snippets:
        # Extract snippet content preview
        content_preview = "New Snippet"
        if s.content and isinstance(s.content, list) and len(s.content) > 0:
            for block in s.content:
                # Assuming block is a dict
                if isinstance(block, dict) and block.get("type") == "text":
                    content_preview = block.get("content", "")
                    break
            # If no text block found, try to use the first block's content or type
            if content_preview == "New Snippet" and isinstance(s.content[0], dict):
                 content_preview = s.content[0].get("content") or s.content[0].get("type", "Media")
                 
        activity_list.append({
            "id": s.id,
            "title": str(content_preview)[:50] if content_preview else "Untitled",
            "type": "snippet",
            "createdAt": s.created_at
        })
    
    # Sort by createdAt descending and take top 5
    activity_list.sort(key=lambda x: x["createdAt"], reverse=True)
    latest_activity = activity_list[:5]
    
    return ApiResponse(data=DashboardStats(
        blogsCount=blogs_count,
        snippetsCount=snippets_count,
        categoriesCount=categories_count,
        tagsCount=tags_count,
        blogsNewThisMonth=blogs_new_this_month,
        snippetsNewThisMonth=snippets_new_this_month,
        latestActivity=latest_activity
    ))

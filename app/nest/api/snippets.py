
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import List
from app.core.database import get_db
from app.models import Snippet
from app.nest.schemas import TimelineGroup, TimelineItem, SnippetDetail
from app.backstage.schemas import ApiResponse
from collections import defaultdict

router = APIRouter()

@router.get("/timeline", response_model=ApiResponse[List[TimelineGroup]], summary="获取日常碎片时间轴")
async def get_snippet_timeline(db: Session = Depends(get_db)):
    """
    获取日常碎片列表，按年份分组返回。
    """
    snippets = db.query(Snippet).order_by(desc(Snippet.created_at)).all()
    
    # Group by year
    grouped = defaultdict(list)
    
    for s in snippets:
        if not s.created_at:
            continue
            
        year = s.created_at.year
        
        # Format content preview
        content_preview = ""
        if s.content and isinstance(s.content, list):
            for block in s.content:
                if isinstance(block, dict) and block.get("type") == "text":
                    content_preview = block.get("content", "")
                    break
        
        # Use subtitle if available, otherwise fallback to content preview
        display_content = s.subtitle if s.subtitle else content_preview
        
        item = TimelineItem(
            blogId=s.id,
            time=s.created_at.strftime("%m-%d"),
            title=s.title if s.title else (content_preview[:20] if content_preview else "无标题"),
            content=display_content[:50] + "..." if len(display_content) > 50 else display_content,
            url=f"/blog/daily?id={s.id}"
        )
        
        grouped[year].append(item)
    
    # Convert to list of TimelineGroup
    result = []
    # Sort years descending
    sorted_years = sorted(grouped.keys(), reverse=True)
    
    for year in sorted_years:
        result.append(TimelineGroup(
            year=year,
            items=grouped[year]
        ))
        
    return ApiResponse(data=result)

@router.get("/{id}", response_model=ApiResponse[SnippetDetail], summary="获取日常碎片详情")
async def get_snippet_detail(id: str, db: Session = Depends(get_db)):
    """
    根据 ID 获取日常碎片详情。
    """
    snippet = db.query(Snippet).filter(Snippet.id == id).first()
    if not snippet:
        raise HTTPException(status_code=404, detail="Snippet not found")
    
    # Increase views
    snippet.views += 1
    db.commit()
    db.refresh(snippet)
    
    metadata = snippet.metadata_info or {}
    
    return ApiResponse(data=SnippetDetail(
        id=snippet.id,
        title=snippet.title,
        subtitle=snippet.subtitle,
        cover=snippet.cover,
        content=snippet.content,
        createdAt=snippet.created_at,
        views=snippet.views,
        tags=[tag.name for tag in snippet.tags],
        date=metadata.get("date"),
        weather=metadata.get("weather"),
        mood=metadata.get("mood"),
        location=metadata.get("location")
    ))

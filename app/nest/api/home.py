from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.models import Blog, Snippet
from app.nest.schemas import LatestArticlesResponse, ArticleItem, LatestSnippetsResponse, SnippetItem
from app.backstage.schemas import ApiResponse

router = APIRouter()

@router.get("/latest-articles", response_model=ApiResponse[LatestArticlesResponse], summary="获取最新文章")
async def get_latest_articles(db: Session = Depends(get_db)):
    """
    获取首页展示的最新文章列表（最多4篇）。
    """
    # Query latest 4 published blogs
    blogs = db.query(Blog).filter(Blog.status == "published").order_by(Blog.created_at.desc()).limit(4).all()
    
    articles = []
    for blog in blogs:
        # Format time
        time_str = blog.created_at.strftime("%Y.%m.%d") if blog.created_at else ""
        
        # Get category name
        category_name = blog.category.name if blog.category else "未分类"
        
        # Get tag names
        tag_names = [tag.name for tag in blog.tags]
        
        articles.append(ArticleItem(
            cover=blog.cover or "",
            title=blog.title,
            subdesc=blog.subtitle or "",
            url=f"/blog?id={blog.id}",
            time=time_str,
            views=blog.views,
            category=category_name,
            tags=tag_names
        ))
        
    return ApiResponse(data=LatestArticlesResponse(
        articles=articles
    ))

@router.get("/latest-snippets", response_model=ApiResponse[LatestSnippetsResponse], summary="获取最新碎片")
async def get_latest_snippets(db: Session = Depends(get_db)):
    """
    获取首页展示的最新日常碎片（最多4篇）。
    """
    # Query latest 4 snippets
    snippets = db.query(Snippet).order_by(Snippet.created_at.desc()).limit(4).all()
    
    diary_cards = []
    for snippet in snippets:
        # Generate bgStyle
        # If cover exists, use it. Else use a placeholder or solid color.
        # Example format: "bg-[url('...')] bg-cover bg-center shadow-accent hover:shadow-gray-500"
        
        bg_url = snippet.cover if snippet.cover else f"https://dummyimage.com/170x304/9c9c9c/fff.png&text={snippet.title}"
        bg_style = f"bg-[url('{bg_url}')] bg-cover bg-center shadow-accent hover:shadow-gray-500"
        
        diary_cards.append(SnippetItem(
            title=snippet.title or "无标题",
            url=f"/blog/daily?id={snippet.id}",
            bgStyle=bg_style,
            textStyle="text-white",
            views=snippet.views
        ))
        
    return ApiResponse(data=LatestSnippetsResponse(
        diaryCards=diary_cards
    ))

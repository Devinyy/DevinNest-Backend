from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func, extract
from typing import List, Optional
from app.core.database import get_db
from app.models import Blog, Category, Tag, blog_tags
from app.backstage.schemas import ApiResponse
from app.nest.schemas import BlogListResponse, BlogListItem, BlogCategory, CategoryStat, TagStat, BlogDetailResponse

router = APIRouter()

@router.get("/list", response_model=ApiResponse[BlogListResponse], summary="获取博客文章列表")
async def get_blog_list(
    page: int = Query(1, ge=1, description="当前页码"),
    pageSize: int = Query(10, ge=1, description="每页条数"),
    categoryId: Optional[str] = Query(None, description="按分类ID筛选"),
    tag: Optional[str] = Query(None, description="按标签名筛选"),
    keyword: Optional[str] = Query(None, description="搜索关键词"),
    year: Optional[int] = Query(None, description="按年份筛选"),
    db: Session = Depends(get_db)
):
    query = db.query(Blog).filter(Blog.status == "published")

    # 筛选条件
    if categoryId:
        query = query.filter(Blog.category_id == categoryId)
    
    if tag:
        # 使用 exists 子查询来优化多对多关联查询
        query = query.filter(Blog.tags.any(Tag.name == tag))
    
    if keyword:
        query = query.filter(
            (Blog.title.ilike(f"%{keyword}%")) | 
            (Blog.subtitle.ilike(f"%{keyword}%")) |
            (Blog.content.ilike(f"%{keyword}%"))
        )
    
    if year:
        query = query.filter(extract('year', Blog.created_at) == year)

    # 排序：按创建时间倒序
    query = query.order_by(Blog.created_at.desc())

    # 计算总数
    total = query.count()
    totalPages = (total + pageSize - 1) // pageSize

    # 分页查询
    blogs = query.offset((page - 1) * pageSize).limit(pageSize).all()

    # 转换数据
    blog_list = []
    for blog in blogs:
        category_data = None
        if blog.category:
            category_data = BlogCategory(id=blog.category.id, name=blog.category.name)
            
        blog_list.append(BlogListItem(
            id=blog.id,
            title=blog.title,
            desc=blog.subtitle or "",
            slug=f"{blog.id}_{blog.title}",
            cover=blog.cover or "",
            date=blog.created_at.strftime("%Y-%m-%d"),
            category=category_data,
            tags=[t.name for t in blog.tags],
            views=blog.views or 0
        ))

    return ApiResponse(data=BlogListResponse(
        list=blog_list,
        total=total,
        totalPages=totalPages,
        currentPage=page
    ))

@router.get("/categories", response_model=ApiResponse[List[CategoryStat]], summary="获取分类统计列表")
async def get_category_stats(db: Session = Depends(get_db)):
    # 统计每个分类下的已发布文章数量
    # 使用 outerjoin 确保即使没有文章的分类也能查出来（count 为 0）
    results = db.query(Category, func.count(Blog.id)).outerjoin(
        Blog, (Category.id == Blog.category_id) & (Blog.status == "published")
    ).group_by(Category.id).all()
    
    stats = []
    for cat, count in results:
        stats.append(CategoryStat(
            id=cat.id,
            name=cat.name,
            count=count,
            icon=cat.icon or ""
        ))
        
    return ApiResponse(data=stats)

@router.get("/tags", response_model=ApiResponse[List[TagStat]], summary="获取热门标签")
async def get_tag_stats(db: Session = Depends(get_db)):
    # 统计每个标签下的已发布文章数量
    # 使用 outerjoin 确保所有标签都能查出来，即使没有关联文章（count 为 0）
    results = db.query(Tag.name, func.count(Blog.id)).outerjoin(
        blog_tags, Tag.id == blog_tags.c.tag_id
    ).outerjoin(
        Blog, (blog_tags.c.blog_id == Blog.id) & (Blog.status == "published")
    ).group_by(Tag.id, Tag.name).order_by(func.count(Blog.id).desc()).all()
    
    stats = []
    for name, count in results:
        stats.append(TagStat(name=name, count=count))
        
    return ApiResponse(data=stats)

@router.get("/{id}", response_model=ApiResponse[BlogDetailResponse], summary="获取博客详情")
async def get_blog_detail(id: str, db: Session = Depends(get_db)):
    blog = db.query(Blog).filter(Blog.id == id, Blog.status == "published").first()
    if not blog:
        raise HTTPException(status_code=404, detail="Blog not found")
    
    # 增加浏览量
    blog.views = (blog.views or 0) + 1
    db.commit()
    db.refresh(blog)
    
    category_data = None
    if blog.category:
        category_data = BlogCategory(id=blog.category.id, name=blog.category.name)
        
    return ApiResponse(data=BlogDetailResponse(
        id=blog.id,
        title=blog.title,
        desc=blog.subtitle or "",
        slug=f"{blog.id}_{blog.title}",
        cover=blog.cover or "",
        date=blog.created_at.strftime("%Y-%m-%d"),
        content=blog.content or "",
        category=category_data,
        tags=[t.name for t in blog.tags],
        views=blog.views
    ))

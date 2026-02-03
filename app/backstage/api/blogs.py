from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from app.backstage.schemas import Blog as BlogSchema, BlogListResponse, BlogCreate, BlogUpdate, Category as CategorySchema, Tag as TagSchema, ApiResponse
from app.core.database import get_db
from app.models import Blog, Category, Tag
from typing import List, Optional

router = APIRouter()

@router.get("", response_model=ApiResponse[BlogListResponse], summary="获取博客列表")
async def get_blogs(
    page: int = 1, 
    pageSize: int = 10, 
    status: Optional[str] = None, 
    keyword: Optional[str] = None, 
    categoryId: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    获取博客列表，支持分页和筛选。
    """
    query = db.query(Blog)
    
    if status:
        query = query.filter(Blog.status == status)
    if keyword:
        query = query.filter(Blog.title.contains(keyword))
    if categoryId:
        query = query.filter(Blog.category_id == categoryId)
        
    total = query.count()
    blogs = query.offset((page - 1) * pageSize).limit(pageSize).all()
    
    # Map to Schema
    result_list = []
    for b in blogs:
        # Ensure category is mapped correctly even if None
        cat_schema = None
        if b.category:
            cat_schema = CategorySchema(
                id=b.category.id, 
                name=b.category.name, 
                icon=b.category.icon, 
                color=b.category.color,
                count=0 # Count not needed here
            )
            
        # Map tags
        tags_schema = [
            TagSchema(id=t.id, name=t.name, color=t.color, count=0) for t in b.tags
        ]
        
        result_list.append(BlogSchema(
            id=b.id,
            title=b.title,
            subtitle=b.subtitle,
            cover=b.cover,
            categoryId=b.category_id or "",
            tagIds=[t.id for t in b.tags],
            status=b.status,
            content=b.content, # Include content or omit for list view optimization
            views=b.views,
            createdAt=b.created_at,
            category=cat_schema,
            tags=tags_schema
        ))
        
    return ApiResponse(data=BlogListResponse(
        list=result_list,
        total=total
    ))

@router.get("/{id}", response_model=ApiResponse[BlogSchema], summary="获取博客详情")
async def get_blog_detail(id: str, db: Session = Depends(get_db)):
    """
    获取博客详情。
    """
    b = db.query(Blog).filter(Blog.id == id).first()
    if not b:
        raise HTTPException(status_code=404, detail="Blog not found")
    
    # Construct response manually to ensure nested objects are populated
    cat_schema = None
    if b.category:
        cat_schema = CategorySchema(
            id=b.category.id, 
            name=b.category.name, 
            icon=b.category.icon, 
            color=b.category.color,
            count=0
        )
        
    tags_schema = [
        TagSchema(id=t.id, name=t.name, color=t.color, count=0) for t in b.tags
    ]
    
    return ApiResponse(data=BlogSchema(
        id=b.id,
        title=b.title,
        subtitle=b.subtitle,
        cover=b.cover,
        categoryId=b.category_id or "",
        tagIds=[t.id for t in b.tags],
        status=b.status,
        content=b.content,
        views=b.views,
        createdAt=b.created_at,
        category=cat_schema,
        tags=tags_schema
    ))

@router.post("", response_model=ApiResponse[BlogSchema], summary="创建博客")
async def create_blog(blog_in: BlogCreate, db: Session = Depends(get_db)):
    """
    创建新的博客文章。
    """
    # Verify Category
    category = db.query(Category).filter(Category.id == blog_in.categoryId).first()
    # If category not found, you might want to raise error or allow None. Assuming strict check:
    # if not category and blog_in.categoryId:
    #    raise HTTPException(status_code=400, detail="Category not found")

    # Verify Tags
    tags = []
    if blog_in.tagIds:
        tags = db.query(Tag).filter(Tag.id.in_(blog_in.tagIds)).all()
    
    new_blog = Blog(
        title=blog_in.title,
        subtitle=blog_in.subtitle,
        content=blog_in.content,
        cover=blog_in.cover,
        status=blog_in.status,
        category_id=blog_in.categoryId if blog_in.categoryId else None,
        tags=tags
    )
    
    db.add(new_blog)
    db.commit()
    db.refresh(new_blog)
    
    # Re-fetch to get relationships populated (or rely on commit refresh, but relationship might need explicit load)
    # Using the same mapping logic as get_detail via pydantic from_orm if Config is set, 
    # but since we are manual, let's return the object which Pydantic will try to validate.
    # To be safe, we reconstruct schema.
    
    cat_schema = None
    if new_blog.category:
        cat_schema = CategorySchema(**new_blog.category.__dict__, count=0)
    
    tags_schema = [TagSchema(**t.__dict__, count=0) for t in new_blog.tags]

    return ApiResponse(data=BlogSchema(
        id=new_blog.id,
        title=new_blog.title,
        subtitle=new_blog.subtitle,
        content=new_blog.content,
        cover=new_blog.cover,
        categoryId=new_blog.category_id or "",
        tagIds=[t.id for t in new_blog.tags],
        status=new_blog.status,
        views=new_blog.views,
        createdAt=new_blog.created_at,
        category=cat_schema,
        tags=tags_schema
    ))

@router.put("/{id}", response_model=ApiResponse[BlogSchema], summary="更新博客")
async def update_blog(id: str, blog_in: BlogUpdate, db: Session = Depends(get_db)):
    """
    更新博客文章。
    """
    blog = db.query(Blog).filter(Blog.id == id).first()
    if not blog:
        raise HTTPException(status_code=404, detail="Blog not found")
    
    # Update fields
    if blog_in.title is not None: blog.title = blog_in.title
    if blog_in.subtitle is not None: blog.subtitle = blog_in.subtitle
    if blog_in.content is not None: blog.content = blog_in.content
    if blog_in.cover is not None: blog.cover = blog_in.cover
    if blog_in.status is not None: blog.status = blog_in.status
    if blog_in.categoryId is not None: blog.category_id = blog_in.categoryId
    
    # Update Tags relationship
    if blog_in.tagIds is not None:
        tags = db.query(Tag).filter(Tag.id.in_(blog_in.tagIds)).all()
        blog.tags = tags
        
    db.commit()
    db.refresh(blog)
    
    cat_schema = None
    if blog.category:
        cat_schema = CategorySchema(**blog.category.__dict__, count=0)
    
    tags_schema = [TagSchema(**t.__dict__, count=0) for t in blog.tags]

    return ApiResponse(data=BlogSchema(
        id=blog.id,
        title=blog.title,
        subtitle=blog.subtitle,
        content=blog.content,
        cover=blog.cover,
        categoryId=blog.category_id or "",
        tagIds=[t.id for t in blog.tags],
        status=blog.status,
        views=blog.views,
        createdAt=blog.created_at,
        category=cat_schema,
        tags=tags_schema
    ))

@router.delete("/{id}", response_model=ApiResponse[dict], summary="删除博客")
async def delete_blog(id: str, db: Session = Depends(get_db)):
    """
    删除博客文章。
    """
    blog = db.query(Blog).filter(Blog.id == id).first()
    if not blog:
        raise HTTPException(status_code=404, detail="Blog not found")
        
    db.delete(blog)
    db.commit()
    return ApiResponse(message="Deleted successfully")

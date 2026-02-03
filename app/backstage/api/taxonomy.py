from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from app.backstage.schemas import Category as CategorySchema, CategoryCreate, CategoryUpdate, Tag as TagSchema, TagCreate, TagUpdate, ApiResponse
from app.core.database import get_db
from app.models import Category, Tag, Blog
from typing import List

router = APIRouter()

# --- Categories ---
@router.get("/categories", response_model=ApiResponse[List[CategorySchema]], summary="获取分类列表")
async def get_categories(db: Session = Depends(get_db)):
    categories = db.query(Category).all()
    # Manual count aggregation (or use subqueries for performance)
    result = []
    for cat in categories:
        count = db.query(Blog).filter(Blog.category_id == cat.id).count()
        result.append(CategorySchema(
            id=cat.id,
            name=cat.name,
            icon=cat.icon,
            color=cat.color,
            count=count
        ))
    return ApiResponse(data=result)

@router.post("/categories", response_model=ApiResponse[CategorySchema], summary="创建分类")
async def create_category(cat_in: CategoryCreate, db: Session = Depends(get_db)):
    existing = db.query(Category).filter(Category.name == cat_in.name).first()
    if existing:
        raise HTTPException(status_code=400, detail="Category already exists")
        
    new_cat = Category(
        name=cat_in.name,
        icon=cat_in.icon,
        color=cat_in.color
    )
    db.add(new_cat)
    db.commit()
    db.refresh(new_cat)
    return ApiResponse(data=CategorySchema(**new_cat.__dict__, count=0))

@router.put("/categories/{id}", response_model=ApiResponse[CategorySchema], summary="更新分类")
async def update_category(id: str, cat_in: CategoryUpdate, db: Session = Depends(get_db)):
    cat = db.query(Category).filter(Category.id == id).first()
    if not cat:
        raise HTTPException(status_code=404, detail="Category not found")
    
    if cat_in.name and cat_in.name != cat.name:
        existing = db.query(Category).filter(Category.name == cat_in.name).first()
        if existing:
            raise HTTPException(status_code=400, detail="Category name already exists")
    
    if cat_in.name:
        cat.name = cat_in.name
    if cat_in.icon:
        cat.icon = cat_in.icon
    if cat_in.color:
        cat.color = cat_in.color
        
    db.commit()
    db.refresh(cat)
    
    # Recalculate count
    count = db.query(Blog).filter(Blog.category_id == cat.id).count()
    return ApiResponse(data=CategorySchema(**cat.__dict__, count=count))

@router.delete("/categories/{id}", response_model=ApiResponse[dict], summary="删除分类")
async def delete_category(id: str, db: Session = Depends(get_db)):
    cat = db.query(Category).filter(Category.id == id).first()
    if not cat:
        raise HTTPException(status_code=404, detail="Category not found")
    
    # Optional: Check if used by blogs? For now, let's set them to null or just delete
    # Blogs with this category will have category_id set to NULL if configured, or we restrict
    # SQLAlchemy default behavior depends on foreign key constraints.
    # Here we just delete the category.
    
    db.delete(cat)
    db.commit()
    return ApiResponse(message="Deleted successfully")

# --- Tags ---
@router.get("/tags", response_model=ApiResponse[List[TagSchema]], summary="获取标签列表")
async def get_tags(db: Session = Depends(get_db)):
    tags = db.query(Tag).all()
    result = []
    for tag in tags:
        # Count blogs using this tag
        count = len(tag.blogs) # This loads all blogs, might be slow for large datasets. Use query.count() on association table for optimized version.
        result.append(TagSchema(
            id=tag.id,
            name=tag.name,
            color=tag.color,
            count=count
        ))
    return ApiResponse(data=result)

@router.post("/tags", response_model=ApiResponse[TagSchema], summary="创建标签")
async def create_tag(tag_in: TagCreate, db: Session = Depends(get_db)):
    existing = db.query(Tag).filter(Tag.name == tag_in.name).first()
    if existing:
        raise HTTPException(status_code=400, detail="Tag already exists")
        
    new_tag = Tag(
        name=tag_in.name,
        color=tag_in.color
    )
    db.add(new_tag)
    db.commit()
    db.refresh(new_tag)
    return ApiResponse(data=TagSchema(**new_tag.__dict__, count=0))

@router.put("/tags/{id}", response_model=ApiResponse[TagSchema], summary="更新标签")
async def update_tag(id: str, tag_in: TagUpdate, db: Session = Depends(get_db)):
    tag = db.query(Tag).filter(Tag.id == id).first()
    if not tag:
        raise HTTPException(status_code=404, detail="Tag not found")
        
    if tag_in.name and tag_in.name != tag.name:
        existing = db.query(Tag).filter(Tag.name == tag_in.name).first()
        if existing:
            raise HTTPException(status_code=400, detail="Tag name already exists")
            
    if tag_in.name:
        tag.name = tag_in.name
    if tag_in.color:
        tag.color = tag_in.color
        
    db.commit()
    db.refresh(tag)
    
    # Recalculate count (approximation or eager load)
    count = len(tag.blogs) 
    return ApiResponse(data=TagSchema(**tag.__dict__, count=count))

@router.delete("/tags/{id}", response_model=ApiResponse[dict], summary="删除标签")
async def delete_tag(id: str, db: Session = Depends(get_db)):
    tag = db.query(Tag).filter(Tag.id == id).first()
    if not tag:
        raise HTTPException(status_code=404, detail="Tag not found")
    
    db.delete(tag)
    db.commit()
    return ApiResponse(message="Deleted successfully")

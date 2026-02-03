from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from app.backstage.schemas import Snippet as SnippetSchema, SnippetCreate, SnippetMetadata, SnippetBlock, ApiResponse
from app.core.database import get_db
from app.models import Snippet, Tag
from typing import List
import uuid

router = APIRouter()

@router.get("", response_model=ApiResponse[List[SnippetSchema]], summary="获取碎片列表")
async def get_snippets(page: int = 1, pageSize: int = 10, db: Session = Depends(get_db)):
    snippets = db.query(Snippet).offset((page - 1) * pageSize).limit(pageSize).all()
    
    result = []
    for s in snippets:
        # Construct schema
        result.append(SnippetSchema(
            id=s.id,
            content=s.content,
            metadata=s.metadata_info,
            tags=[t.name for t in s.tags] # Schema expects list of strings for tags
        ))
    return ApiResponse(data=result)

@router.get("/{id}", response_model=ApiResponse[SnippetSchema], summary="获取碎片详情")
async def get_snippet_detail(id: str, db: Session = Depends(get_db)):
    s = db.query(Snippet).filter(Snippet.id == id).first()
    if not s:
        raise HTTPException(status_code=404, detail="Snippet not found")
        
    return ApiResponse(data=SnippetSchema(
        id=s.id,
        content=s.content,
        metadata=s.metadata_info,
        tags=[t.name for t in s.tags]
    ))

@router.post("", response_model=ApiResponse[SnippetSchema], summary="创建碎片")
async def create_snippet(snippet_in: SnippetCreate, db: Session = Depends(get_db)):
    # Handle Tags: For snippets, schema says tags: List[str]. 
    # We should find existing tags by name or create new ones? 
    # Or assume they refer to existing tags? 
    # Usually "tags" as strings implies simple tagging. 
    # Let's assume we match by name, create if not exists for simplicity or just match existing.
    # Given the previous pattern, let's assume we map to existing tags or ignore.
    # However, user input is List[str] (names) not IDs.
    
    tag_objs = []
    if snippet_in.tags:
        for tag_name in snippet_in.tags:
            tag = db.query(Tag).filter(Tag.name == tag_name).first()
            if not tag:
                # Auto-create tag if it doesn't exist? Or skip?
                # Let's auto-create for snippets flexibility
                tag = Tag(name=tag_name, color="blue") # Default color
                db.add(tag)
                db.commit() # Commit to get ID
                db.refresh(tag)
            tag_objs.append(tag)
            
    # Prepare JSON content
    # snippet_in.content is List[SnippetBlock], Pydantic models need to be dumped to dict/json for JSON column
    content_json = [block.dict() for block in snippet_in.content]
    metadata_json = snippet_in.metadata.dict()
    metadata_json['date'] = metadata_json['date'].isoformat() # Handle datetime serialization if needed, though Pydantic .dict() usually keeps objects. SQLAlchemy JSON might need primitives. 
    # Actually SQLAlchemy with SQLite/JSON handles basic types. Datetime might be tricky.
    # Let's ensure primitives.
    
    new_snippet = Snippet(
        content=content_json,
        metadata_info=metadata_json,
        tags=tag_objs
    )
    
    db.add(new_snippet)
    db.commit()
    db.refresh(new_snippet)
    
    return ApiResponse(data=SnippetSchema(
        id=new_snippet.id,
        content=new_snippet.content,
        metadata=new_snippet.metadata_info,
        tags=[t.name for t in new_snippet.tags]
    ))

@router.put("/{id}", response_model=ApiResponse[SnippetSchema], summary="更新碎片")
async def update_snippet(id: str, snippet_in: SnippetCreate, db: Session = Depends(get_db)):
    s = db.query(Snippet).filter(Snippet.id == id).first()
    if not s:
        raise HTTPException(status_code=404, detail="Snippet not found")
        
    # Update fields
    s.content = [block.dict() for block in snippet_in.content]
    
    metadata_json = snippet_in.metadata.dict()
    metadata_json['date'] = metadata_json['date'].isoformat()
    s.metadata_info = metadata_json
    
    # Update tags
    if snippet_in.tags is not None:
        tag_objs = []
        for tag_name in snippet_in.tags:
            tag = db.query(Tag).filter(Tag.name == tag_name).first()
            if not tag:
                tag = Tag(name=tag_name, color="blue")
                db.add(tag)
                db.commit()
                db.refresh(tag)
            tag_objs.append(tag)
        s.tags = tag_objs
        
    db.commit()
    db.refresh(s)
    
    return ApiResponse(data=SnippetSchema(
        id=s.id,
        content=s.content,
        metadata=s.metadata_info,
        tags=[t.name for t in s.tags]
    ))

@router.delete("/{id}", response_model=ApiResponse[dict], summary="删除碎片")
async def delete_snippet(id: str, db: Session = Depends(get_db)):
    s = db.query(Snippet).filter(Snippet.id == id).first()
    if not s:
        raise HTTPException(status_code=404, detail="Snippet not found")
        
    db.delete(s)
    db.commit()
    return ApiResponse(message="Deleted successfully")

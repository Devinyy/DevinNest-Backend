from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from sqlalchemy.orm import Session
from app.backstage.schemas import Snippet as SnippetSchema, SnippetCreate, SnippetUpdate, SnippetMetadata, SnippetBlock, ApiResponse, DeleteRequest
from app.core.database import get_db
from app.models import Snippet, Tag
from typing import List
import uuid
import os
import re
import json
from pathlib import Path

router = APIRouter()

# --- File Sync Helpers ---
BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
STATIC_BLOGS_DIR = BASE_DIR / "static" / "blogs"

def get_snippet_filename(id: str, title: str) -> str:
    # Use title if available, else id
    display_title = title if title else id
    # Sanitize title
    safe_title = re.sub(r'[\\/*?:"<>|]', '_', display_title)
    
    # If id already starts with "snippet_", don't add prefix again
    if id.startswith("snippet_"):
        return f"{id}_{safe_title}.md"
    
    return f"snippet_{id}_{safe_title}.md"

def convert_snippet_to_markdown(snippet: Snippet) -> str:
    # Extract metadata
    title = snippet.title or "Untitled Snippet"
    date_str = snippet.created_at.strftime("%Y-%m-%d %H:%M:%S")
    tags = [t.name for t in snippet.tags]
    tags_str = json.dumps(tags, ensure_ascii=False)
    
    # Frontmatter
    md = "---\n"
    md += f"id: {snippet.id}\n"
    md += f"title: {title}\n"
    md += f"date: {date_str}\n"
    md += f"tags: {tags_str}\n"
    md += "category: Snippet\n"
    if snippet.cover:
        md += f"cover: {snippet.cover}\n"
    md += "---\n\n"
    
    # Content
    if snippet.content and isinstance(snippet.content, list):
        for block in snippet.content:
            if not isinstance(block, dict):
                continue
                
            b_type = block.get("type")
            b_content = block.get("content", "")
            
            if b_type == "text":
                md += f"{b_content}\n\n"
            elif b_type == "image":
                src = block.get("src", "")
                caption = block.get("caption", "")
                md += f"![{caption}]({src})\n"
                if caption:
                    md += f"*{caption}*\n"
                md += "\n"
            elif b_type == "quote":
                author = block.get("author", "")
                md += f"> {b_content}\n"
                if author:
                    md += f"> — {author}\n"
                md += "\n"
            elif b_type == "gallery":
                images = block.get("images", [])
                if images:
                    md += "**Gallery:**\n\n"
                    for img in images:
                        md += f"![Gallery Image]({img})\n"
                    md += "\n"
                    
    return md

def sync_snippet_file(snippet: Snippet):
    try:
        if not STATIC_BLOGS_DIR.exists():
            STATIC_BLOGS_DIR.mkdir(parents=True, exist_ok=True)
            
        filename = get_snippet_filename(snippet.id, snippet.title)
        file_path = STATIC_BLOGS_DIR / filename
        
        content = convert_snippet_to_markdown(snippet)
        
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
            
    except Exception as e:
        print(f"Error syncing snippet file: {e}")

def remove_snippet_file(id: str, title: str):
    try:
        filename = get_snippet_filename(id, title)
        file_path = STATIC_BLOGS_DIR / filename
        if file_path.exists():
            os.remove(file_path)
    except Exception as e:
        print(f"Error removing snippet file: {e}")

@router.post("/sync-md-files", response_model=ApiResponse[dict], summary="同步所有碎片MD文件")
async def sync_all_md_files(background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    """
    手动触发同步所有碎片的Markdown文件到 /static/blogs/ 目录。
    """
    snippets = db.query(Snippet).all()
    count = 0
    for s in snippets:
        background_tasks.add_task(sync_snippet_file, s)
        count += 1
        
    return ApiResponse(message=f"Started syncing {count} snippets")

@router.get("", response_model=ApiResponse[List[SnippetSchema]], summary="获取碎片列表")
async def get_snippets(page: int = 1, pageSize: int = 10, db: Session = Depends(get_db)):
    snippets = db.query(Snippet).offset((page - 1) * pageSize).limit(pageSize).all()
    
    result = []
    for s in snippets:
        # Construct schema
        result.append(SnippetSchema(
            id=s.id,
            title=s.title,
            subtitle=s.subtitle,
            cover=s.cover,
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
        title=s.title,
        subtitle=s.subtitle,
        cover=s.cover,
        content=s.content,
        metadata=s.metadata_info,
        tags=[t.name for t in s.tags]
    ))

@router.post("/create", response_model=ApiResponse[SnippetSchema], summary="创建碎片")
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
    
    # Generate ID: snippet_000001
    existing_ids = db.query(Snippet.id).filter(Snippet.id.like("snippet_%")).all()
    max_n = 0
    for (sid,) in existing_ids:
        try:
            parts = sid.split('_')
            if len(parts) == 2 and parts[1].isdigit():
                n = int(parts[1])
                if n > max_n:
                    max_n = n
        except:
            pass
            
    new_id = f"snippet_{max_n + 1:06d}"

    new_snippet = Snippet(
        id=new_id,
        title=snippet_in.title,
        subtitle=snippet_in.subtitle,
        cover=snippet_in.cover,
        content=content_json,
        metadata_info=metadata_json,
        tags=tag_objs
    )
    
    db.add(new_snippet)
    db.commit()
    db.refresh(new_snippet)
    
    # Sync MD file
    sync_snippet_file(new_snippet)
    
    return ApiResponse(data=SnippetSchema(
        id=new_snippet.id,
        title=new_snippet.title,
        subtitle=new_snippet.subtitle,
        cover=new_snippet.cover,
        content=new_snippet.content,
        metadata=new_snippet.metadata_info,
        tags=[t.name for t in new_snippet.tags]
    ))

@router.post("/update", response_model=ApiResponse[SnippetSchema], summary="更新碎片")
async def update_snippet(snippet_in: SnippetUpdate, db: Session = Depends(get_db)):
    id = snippet_in.id
    s = db.query(Snippet).filter(Snippet.id == id).first()
    if not s:
        raise HTTPException(status_code=404, detail="Snippet not found")
        
    # Store old title for file renaming
    old_title = s.title

    # Update fields
    s.title = snippet_in.title
    s.subtitle = snippet_in.subtitle
    s.cover = snippet_in.cover
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
    
    # Sync MD file
    if old_title != s.title:
        remove_snippet_file(s.id, old_title)
        
    sync_snippet_file(s)
    
    return ApiResponse(data=SnippetSchema(
        id=s.id,
        title=s.title,
        subtitle=s.subtitle,
        cover=s.cover,
        content=s.content,
        metadata=s.metadata_info,
        tags=[t.name for t in s.tags]
    ))

@router.post("/delete", response_model=ApiResponse[dict], summary="删除碎片")
async def delete_snippet(req: DeleteRequest, db: Session = Depends(get_db)):
    id = req.id
    s = db.query(Snippet).filter(Snippet.id == id).first()
    if not s:
        raise HTTPException(status_code=404, detail="Snippet not found")
        
    db.delete(s)
    db.commit()
    
    # Remove MD file
    remove_snippet_file(s.id, s.title)
    
    return ApiResponse(message="Deleted successfully")

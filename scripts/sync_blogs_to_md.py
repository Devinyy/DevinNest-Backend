
import sys
import os
from pathlib import Path

# Add project root to path
project_root = "/Users/zhangxiang/my_project/DevinNest-Backend"
sys.path.append(project_root)

from app.core.database import SessionLocal
from app.models import Blog
from app.backstage.api.blogs import sync_blog_file

def sync_all():
    db = SessionLocal()
    try:
        blogs = db.query(Blog).all()
        print(f"Found {len(blogs)} blogs. Syncing...")
        for blog in blogs:
            print(f"Syncing blog: {blog.title}")
            sync_blog_file(blog.id, blog.title, blog.content)
        print("Sync complete.")
    finally:
        db.close()

if __name__ == "__main__":
    sync_all()

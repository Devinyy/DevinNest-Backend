
import sys
import os
from pathlib import Path

# Add project root to path
project_root = "/Users/zhangxiang/my_project/DevinNest-Backend"
sys.path.append(project_root)

from app.core.database import SessionLocal
from app.models import Snippet
from app.backstage.api.snippets import sync_snippet_file, STATIC_BLOGS_DIR

def sync_all():
    db = SessionLocal()
    try:
        snippets = db.query(Snippet).all()
        print(f"Found {len(snippets)} snippets. Syncing to {STATIC_BLOGS_DIR}...")
        for s in snippets:
            print(f"Syncing snippet: {s.title} ({s.id})")
            sync_snippet_file(s)
        print("Sync complete.")
    finally:
        db.close()

if __name__ == "__main__":
    sync_all()

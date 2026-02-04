
import sys
import os
from pathlib import Path

# Add project root to path
project_root = "/Users/zhangxiang/my_project/DevinNest-Backend"
sys.path.append(project_root)

from app.backstage.api.blogs import sync_blog_file, get_blog_filename, STATIC_BLOGS_DIR

print(f"Static Blogs Dir: {STATIC_BLOGS_DIR}")

# Test sync
blog_id = "test-id"
title = "Test Blog Title / With Special Chars"
content = "# Hello World\nThis is a test."

sync_blog_file(blog_id, title, content)

filename = get_blog_filename(blog_id, title)
file_path = STATIC_BLOGS_DIR / filename

if file_path.exists():
    print(f"File created successfully: {file_path}")
    with open(file_path, "r") as f:
        print("Content:", f.read())
    
    # Cleanup
    os.remove(file_path)
    print("Cleanup done.")
else:
    print("File not created!")

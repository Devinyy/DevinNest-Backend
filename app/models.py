from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey, Table, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base
import uuid

# Helper to generate UUID string
def generate_uuid():
    return str(uuid.uuid4())

# Association Tables
blog_tags = Table(
    "blog_tags",
    Base.metadata,
    Column("blog_id", String, ForeignKey("blogs.id")),
    Column("tag_id", String, ForeignKey("tags.id"))
)

snippet_tags = Table(
    "snippet_tags",
    Base.metadata,
    Column("snippet_id", String, ForeignKey("snippets.id")),
    Column("tag_id", String, ForeignKey("tags.id"))
)

# Models
class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, default=generate_uuid)
    username = Column(String, unique=True, index=True)
    password_hash = Column(String)
    avatar = Column(String)

class Category(Base):
    __tablename__ = "categories"

    id = Column(String, primary_key=True, default=generate_uuid)
    name = Column(String, unique=True, index=True)
    icon = Column(String, nullable=True)
    color = Column(String, nullable=True)
    
    blogs = relationship("Blog", back_populates="category")

class Tag(Base):
    __tablename__ = "tags"

    id = Column(String, primary_key=True, default=generate_uuid)
    name = Column(String, unique=True, index=True)
    color = Column(String, nullable=True)
    
    blogs = relationship("Blog", secondary=blog_tags, back_populates="tags")
    snippets = relationship("Snippet", secondary=snippet_tags, back_populates="tags")

class Blog(Base):
    __tablename__ = "blogs"

    id = Column(String, primary_key=True)
    title = Column(String, index=True)
    subtitle = Column(String, nullable=True)
    content = Column(Text, nullable=True)
    cover = Column(String, nullable=True)
    status = Column(String, default="draft") # draft, published
    views = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    category_id = Column(String, ForeignKey("categories.id"), nullable=True)
    category = relationship("Category", back_populates="blogs")
    
    tags = relationship("Tag", secondary=blog_tags, back_populates="blogs")

class Snippet(Base):
    __tablename__ = "snippets"

    id = Column(String, primary_key=True)
    content = Column(JSON) # Stores List[SnippetBlock]
    metadata_info = Column(JSON, name="metadata") # Stores SnippetMetadata. Renamed to avoid reserved word conflict if any, though metadata is fine in SQLAlchemy but mapped to metadata_info
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    tags = relationship("Tag", secondary=snippet_tags, back_populates="snippets")

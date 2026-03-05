from pydantic import BaseModel, Field
from typing import List, Optional, Any, Generic, TypeVar
from datetime import datetime

T = TypeVar('T')

# --- Common Response Model ---
class ApiResponse(BaseModel, Generic[T]):
    code: int = 200
    message: str = "success"
    data: Optional[T] = None

class DeleteRequest(BaseModel):
    id: str

# --- Auth ---
class LoginRequest(BaseModel):
    username: str
    password: str

class UserInfo(BaseModel):
    id: str
    username: str
    avatar: str

class LoginResponse(BaseModel):
    token: str
    userInfo: UserInfo

# --- Dashboard ---
class DashboardStats(BaseModel):
    blogsCount: int
    snippetsCount: int
    categoriesCount: int
    tagsCount: int
    blogsNewThisMonth: int
    snippetsNewThisMonth: int
    latestActivity: Optional[List[Any]] = None

# --- Taxonomy ---
class CategoryBase(BaseModel):
    name: str
    icon: Optional[str] = None
    color: Optional[str] = None

class Category(CategoryBase):
    id: str
    count: int = 0

class CategoryCreate(CategoryBase):
    pass

class CategoryUpdate(CategoryBase):
    id: str
    name: Optional[str] = None

class TagBase(BaseModel):
    name: str
    color: Optional[str] = None

class Tag(TagBase):
    id: str
    count: int = 0

class TagCreate(TagBase):
    pass

class TagUpdate(TagBase):
    id: str
    name: Optional[str] = None

# --- Blogs ---
class BlogBase(BaseModel):
    title: str
    subtitle: Optional[str] = None
    cover: Optional[str] = None
    categoryId: str
    tagIds: List[str] = []
    status: str = "draft" # draft, published

class BlogCreate(BlogBase):
    content: str

class BlogUpdate(BlogBase):
    id: str
    content: Optional[str] = None

class Blog(BlogBase):
    id: str
    content: Optional[str] = None # Content might not be in list view
    views: int = 0
    createdAt: datetime
    # Expanded objects for response
    category: Optional[Category] = None
    tags: List[Tag] = []

class BlogListResponse(BaseModel):
    list: List[Blog]
    total: int

# --- Snippets ---
class SnippetBlock(BaseModel):
    type: str # text, image, quote, gallery
    content: Optional[str] = None
    src: Optional[str] = None
    caption: Optional[str] = None
    author: Optional[str] = None
    images: Optional[List[str]] = None # For gallery type

class SnippetMetadata(BaseModel):
    weather: Optional[str] = None
    mood: Optional[str] = None
    location: Optional[str] = None
    date: datetime

class SnippetCreate(BaseModel):
    title: Optional[str] = None
    subtitle: Optional[str] = None
    cover: Optional[str] = None
    content: List[SnippetBlock]
    metadata: SnippetMetadata
    tags: List[str] = []

class SnippetUpdate(SnippetCreate):
    id: str

class Snippet(SnippetCreate):
    id: str

# --- Common ---
class UploadResponse(BaseModel):
    url: str
    filename: str
    path: str # Added path field

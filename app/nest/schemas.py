from typing import List, Optional, Any
from pydantic import BaseModel
from datetime import datetime

class Project(BaseModel):
    id: int
    name: str
    description: str
    owner: str

class BlogCategory(BaseModel):
    id: str
    name: str

class BlogListItem(BaseModel):
    id: str
    title: str
    desc: Optional[str] = ""
    slug: str
    cover: Optional[str] = ""
    date: str
    category: Optional[BlogCategory] = None
    tags: List[str] = []
    views: int = 0

class BlogDetailResponse(BaseModel):
    id: str
    title: str
    desc: Optional[str] = ""
    slug: str
    cover: Optional[str] = ""
    date: str
    content: str
    category: Optional[BlogCategory] = None
    tags: List[str] = []
    views: int = 0

class BlogListResponse(BaseModel):
    list: List[BlogListItem]
    total: int
    totalPages: int
    currentPage: int

class CategoryStat(BaseModel):
    id: str
    name: str
    count: int
    icon: Optional[str] = ""

class TagStat(BaseModel):
    name: str
    count: int

# Home API Schemas
class ArticleItem(BaseModel):
    cover: Optional[str] = ""
    title: str
    subdesc: Optional[str] = ""
    url: str
    time: str
    views: int = 0
    category: Optional[str] = ""
    tags: List[str] = []

class LatestArticlesResponse(BaseModel):
    title: str = "最新"
    url: str = "/blog"
    articles: List[ArticleItem]

class SnippetItem(BaseModel):
    title: str
    url: str
    bgStyle: str
    textStyle: str = "text-white"
    views: int = 0

class LatestSnippetsResponse(BaseModel):
    diaryCards: List[SnippetItem]

class TimelineItem(BaseModel):
    blogId: str
    time: str
    title: str
    content: Optional[str] = None
    url: Optional[str] = None

class TimelineGroup(BaseModel):
    year: int
    items: List[TimelineItem]

class SnippetDetail(BaseModel):
    id: str
    title: Optional[str] = None
    subtitle: Optional[str] = None
    cover: Optional[str] = None
    content: Optional[List[Any]] = None
    createdAt: datetime
    views: int = 0
    tags: List[str] = []
    
    # Metadata fields
    date: Optional[datetime] = None
    weather: Optional[str] = None
    mood: Optional[str] = None
    location: Optional[str] = None



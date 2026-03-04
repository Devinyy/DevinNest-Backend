from pydantic import BaseModel
from typing import List, Optional

class Project(BaseModel):
    id: int
    name: str
    description: str
    owner: str

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

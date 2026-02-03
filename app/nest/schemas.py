from pydantic import BaseModel
from typing import List

class Project(BaseModel):
    id: int
    name: str
    description: str
    owner: str

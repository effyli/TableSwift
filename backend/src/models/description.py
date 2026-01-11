from pydantic import BaseModel
from .labels import Labels
from typing import Optional, List

class Description(BaseModel):
    id: Optional[int] = None
    description: str
    version: Optional[int] = None
    labels: Optional[List[Labels]] = None

    
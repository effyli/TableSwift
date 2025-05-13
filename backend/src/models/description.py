from pydantic import BaseModel
from .labels import Labels
from typing import Optional

class Description(BaseModel):
    id: Optional[int] = None
    description: str
    version: Optional[int] = None
    labels: Optional[Labels] = None

    
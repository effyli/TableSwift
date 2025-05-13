from pydantic import BaseModel, Json
from typing import List
from .code import Code

class Labels(BaseModel):
    id: int
    json: Json
    codes: List[Code]

from pydantic import BaseModel
from typing import List, Dict, Any, Optional

class CreateFile(BaseModel):
    file_path: str

class File(BaseModel):
    file_path: str
    data: Optional[List[Dict[str, Any]]] = None
    total_rows: Optional[int] = None
    loaded_rows: Optional[int] = None
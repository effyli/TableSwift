from pydantic import BaseModel

class Code(BaseModel):
    id: int
    code: str
    version: int


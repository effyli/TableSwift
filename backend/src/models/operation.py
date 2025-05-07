from pydantic import BaseModel

class Operation(BaseModel):
    id: int
    name: str

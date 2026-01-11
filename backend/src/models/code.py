from pydantic import BaseModel

class Code(BaseModel):
    id: int
    code: str
    router_code: str
    version: int


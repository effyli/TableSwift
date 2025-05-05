from pydantic import BaseModel

class CreateFile(BaseModel):
    file_path: str

class File(BaseModel):
    file_path: str
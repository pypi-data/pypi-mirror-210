from pydantic import BaseModel


class Path(BaseModel):
    path: str
    name: str

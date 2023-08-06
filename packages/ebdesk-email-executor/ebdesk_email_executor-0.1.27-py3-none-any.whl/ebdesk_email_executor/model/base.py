from pydantic import BaseModel
from typing import List


class Email(BaseModel):
    email: str
    password: str
    status: str = "ACTIVE"
    active: bool = False


class ListEmail(BaseModel):
    data: List[Email]

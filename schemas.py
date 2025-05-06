from pydantic import BaseModel
from typing import List

class AuthorBase(BaseModel):
    name: str

class AuthorCreate(AuthorBase):
    pass

class Author(AuthorBase):
    id: int

    class Config:
        orm_mode = True

class PaperBase(BaseModel):
    title: str
    abstract: str
    arxiv_id: str
    link: str

class PaperCreate(PaperBase):
    embedding: list
    authors: List[str]

class Paper(PaperBase):
    id: int
    embedding: list
    authors: List[Author]

    class Config:
        orm_mode = True

class PaperSummary(BaseModel):
    title: str
    abstract: str
    arxiv_id: str
    link: str
    score: float

    class Config:
        orm_mode = True

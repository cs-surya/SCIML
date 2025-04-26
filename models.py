from sqlalchemy import Column, Integer, String, Table, ForeignKey, JSON
from sqlalchemy.orm import relationship
from database import Base

paper_author = Table(
    "paper_author",
    Base.metadata,
    Column("paper_id", Integer, ForeignKey("papers.id")),
    Column("author_id", Integer, ForeignKey("authors.id"))
)

class Paper(Base):
    __tablename__ = "papers"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    abstract = Column(String)
    arxiv_id = Column(String, unique=True, index=True)
    link = Column(String)
    embedding = Column(JSON)

    authors = relationship("Author", secondary=paper_author, back_populates="papers")

class Author(Base):
    __tablename__ = "authors"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)

    papers = relationship("Paper", secondary=paper_author, back_populates="authors")
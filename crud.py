from sqlalchemy.orm import Session
import models, schemas

def get_author_by_name(db: Session, name: str):
    return db.query(models.Author).filter(models.Author.name == name).first()

def create_author(db: Session, author: schemas.AuthorCreate):
    db_author = models.Author(name=author.name)
    db.add(db_author)
    db.commit()
    db.refresh(db_author)
    return db_author

def get_paper_by_arxiv_id(db: Session, arxiv_id: str):
    return db.query(models.Paper).filter(models.Paper.arxiv_id == arxiv_id).first()

def create_paper(db: Session, paper: schemas.PaperCreate):
    if get_paper_by_arxiv_id(db, paper.arxiv_id):
        return None
    db_paper = models.Paper(
        title=paper.title,
        abstract=paper.abstract,
        arxiv_id=paper.arxiv_id,
        link=paper.link,
        embedding=paper.embedding
    )
    db.add(db_paper)
    db.commit()
    db.refresh(db_paper)
    for author_name in paper.authors:
        db_author = get_author_by_name(db, author_name)
        if not db_author:
            db_author = models.Author(name=author_name)
            db.add(db_author)
            db.commit()
            db.refresh(db_author)
        db_paper.authors.append(db_author)
    db.commit()
    db.refresh(db_paper)
    return db_paper

def get_papers(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Paper).offset(skip).limit(limit).all()

def get_authors(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Author).offset(skip).limit(limit).all()
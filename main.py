from fastapi import FastAPI, HTTPException, Depends
from typing import List
import numpy as np

import embedding_model
import crud
import schemas
from database import SessionLocal, engine, Base
from sqlalchemy.orm import Session
from fastapi.middleware.cors import CORSMiddleware

# create DB tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="ArXiv Physics Embeddings API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/embed/", response_model=List[schemas.Paper])
def create_embeddings(
    query: str,
    max_results: int = 10,
    db: Session = Depends(get_db)
):
    papers = embedding_model.fetch_papers(query, max_results)
    created = []
    for p in papers:
        if crud.get_paper_by_arxiv_id(db, p.entry_id):
            continue
        emb = embedding_model.compute_embedding(p.title + " " + p.summary)
        paper_in = schemas.PaperCreate(
            title=p.title,
            abstract=p.summary,
            arxiv_id=p.entry_id,
            link=p.entry_id,
            embedding=emb,
            authors=[a.name for a in p.authors]
        )
        db_paper = crud.create_paper(db, paper_in)
        if db_paper:
            created.append(db_paper)

    if not created:
        raise HTTPException(400, "No new papers to embed")
    return created

@app.get("/papers/", response_model=List[schemas.Paper])
def read_papers(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    return crud.get_papers(db, skip, limit)

@app.get("/search/", response_model=List[schemas.PaperSummary])
def search_papers(
    query: str,
    top: int = 5,
    min_score: float = 0.0,
    db: Session = Depends(get_db)
):
    def _cosine_search() -> List[tuple]:
        papers = crud.get_papers(db)
        q_emb = np.array(embedding_model.compute_embedding(query))
        scored = []
        for p in papers:
            emb = np.array(p.embedding)
            sim = float(q_emb.dot(emb) / (np.linalg.norm(q_emb) * np.linalg.norm(emb)))
            if sim >= min_score:
                scored.append((p, sim))
        scored.sort(key=lambda x: x[1], reverse=True)
        return scored[:top]

    # 1) first pass
    hits = _cosine_search()

    # 2) if no hits above threshold, ingest new papers and retry
    if not hits:
        new_papers = embedding_model.fetch_papers(query, max_results=10)
        for p in new_papers:
            if crud.get_paper_by_arxiv_id(db, p.entry_id):
                continue
            emb = embedding_model.compute_embedding(p.title + " " + p.summary)
            paper_in = schemas.PaperCreate(
                title=p.title,
                abstract=p.summary,
                arxiv_id=p.entry_id,
                link=p.entry_id,
                embedding=emb,
                authors=[a.name for a in p.authors]
            )
            crud.create_paper(db, paper_in)

        hits = _cosine_search()

    if not hits:
        raise HTTPException(404, "No matching papers found even after ingest")

    # 3) format response
    return [
        schemas.PaperSummary(
            title=paper.title,
            abstract=paper.abstract,
            arxiv_id=paper.arxiv_id,
            link=paper.link,
            score=score
        )
        for paper, score in hits
    ]

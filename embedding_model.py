import arxiv
from sentence_transformers import SentenceTransformer

model = SentenceTransformer('all-MiniLM-L6-v2')

def fetch_papers(query: str = "cat:physics", max_results: int = 10):
    search = arxiv.Search(query=query, max_results=max_results)
    return list(search.results())

def compute_embedding(text: str):
    return model.encode(text).tolist()
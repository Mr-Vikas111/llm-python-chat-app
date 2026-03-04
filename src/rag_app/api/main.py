from fastapi import FastAPI

from rag_app.api.schemas import IngestResponse, QueryRequest, QueryResponse, RetrievedChunk
from rag_app.core.config import get_settings
from rag_app.core.generator import generate_answer
from rag_app.core.retriever import retrieve
from rag_app.ingestion.pipeline import ingest_from_raw_data

settings = get_settings()
app = FastAPI(title=settings.app_name)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "env": settings.app_env}


@app.post("/ingest", response_model=IngestResponse)
def ingest() -> IngestResponse:
    result = ingest_from_raw_data()
    return IngestResponse(**result)


@app.post("/query", response_model=QueryResponse)
def query(payload: QueryRequest) -> QueryResponse:
    chunks = retrieve(query=payload.question, top_k=payload.top_k)
    answer = generate_answer(question=payload.question, chunks=chunks)
    return QueryResponse(answer=answer, chunks=[RetrievedChunk(**item) for item in chunks])

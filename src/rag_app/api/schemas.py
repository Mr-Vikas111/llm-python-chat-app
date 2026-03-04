from pydantic import BaseModel, Field


class IngestResponse(BaseModel):
    files: int
    chunks: int
    indexed: int


class QueryRequest(BaseModel):
    question: str = Field(min_length=3)
    top_k: int | None = Field(default=None, ge=1, le=20)


class RetrievedChunk(BaseModel):
    text: str
    source: str
    chunk_index: str
    similarity_score: float | None = None


class QueryResponse(BaseModel):
    answer: str
    chunks: list[RetrievedChunk]

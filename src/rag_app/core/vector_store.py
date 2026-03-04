from functools import lru_cache
from uuid import uuid4

from langchain_chroma import Chroma
from langchain_core.documents import Document

from rag_app.core.config import get_settings
from rag_app.core.embeddings import get_embedding_model


@lru_cache(maxsize=1)
def get_vector_store() -> Chroma:
    """Get or create ChromaDB vector store with LangChain."""
    settings = get_settings()
    embeddings = get_embedding_model()
    
    return Chroma(
        collection_name=settings.collection_name,
        embedding_function=embeddings,
        persist_directory=str(settings.vector_db_dir),
    )


def upsert_documents(texts: list[str], metadata: list[dict[str, str]]) -> int:
    """Add or update documents in the vector store."""
    if not texts:
        return 0
    
    # Create LangChain Document objects
    documents = [
        Document(
            page_content=text,
            metadata=meta,
        )
        for text, meta in zip(texts, metadata)
    ]
    
    # Add documents to vector store
    vector_store = get_vector_store()
    vector_store.add_documents(documents)
    
    return len(documents)


def similarity_search(query: str, top_k: int) -> list[dict]:
    """Search for similar documents using semantic similarity."""
    vector_store = get_vector_store()
    
    # Perform similarity search with scores
    docs_with_scores = vector_store.similarity_search_with_score(query, k=top_k)
    
    # Convert results to the expected format
    results = []
    for doc, score in docs_with_scores:
        results.append({
            "text": doc.page_content,
            "source": doc.metadata.get("source", "unknown"),
            "chunk_index": doc.metadata.get("chunk_index", "0"),
            "similarity_score": float(score),  # Chroma returns distance, lower is better
        })
    
    return results


def mmr_search(query: str, top_k: int, fetch_k: int = 20, lambda_mult: float = 0.5) -> list[dict]:
    """
    Search using Maximal Marginal Relevance (MMR).
    
    MMR balances relevance with diversity by selecting documents that are:
    1. Highly relevant to the query
    2. Diverse from each other (reduces redundancy)
    
    Args:
        query: Search query string
        top_k: Number of documents to return
        fetch_k: Number of documents to fetch before applying MMR (should be > top_k)
        lambda_mult: Parameter controlling diversity vs relevance (0.0-1.0)
                    - 0.0: Maximum diversity (least redundant)
                    - 1.0: Maximum relevance (like standard similarity)
    
    Returns:
        List of documents with metadata, sorted by MMR score
    """
    vector_store = get_vector_store()
    
    # Perform MMR search
    docs = vector_store.max_marginal_relevance_search(
        query,
        k=top_k,
        fetch_k=fetch_k,
        lambda_mult=lambda_mult,
    )
    
    # Convert results to the expected format
    results = []
    for i, doc in enumerate(docs):
        results.append({
            "text": doc.page_content,
            "source": doc.metadata.get("source", "unknown"),
            "chunk_index": doc.metadata.get("chunk_index", "0"),
            "similarity_score": 1.0 - (i / len(docs)) if docs else 0.0,  # Approximate score based on rank
            "retrieval_method": "mmr",
        })
    
    return results

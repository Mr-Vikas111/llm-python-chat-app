from rag_app.core.chunker import split_text
from rag_app.core.config import get_settings
from rag_app.core.vector_store import upsert_documents
from rag_app.ingestion.loaders import collect_documents


def ingest_from_raw_data() -> dict[str, int]:
    """Ingest documents from raw data directory into the vector store."""
    settings = get_settings()
    docs = collect_documents(settings.raw_data_dir)

    all_texts: list[str] = []
    all_meta: list[dict[str, str]] = []

    for source, content in docs:
        chunks = split_text(
            text=content,
            source=source,
            chunk_size=settings.chunk_size,
            chunk_overlap=settings.chunk_overlap,
        )
        for chunk in chunks:
            all_texts.append(chunk.text)
            all_meta.append({"source": chunk.source, "chunk_index": str(chunk.index)})

    if not all_texts:
        return {"files": len(docs), "chunks": 0, "indexed": 0}

    # LangChain's Chroma handles embeddings internally
    indexed = upsert_documents(texts=all_texts, metadata=all_meta)
    return {"files": len(docs), "chunks": len(all_texts), "indexed": indexed}

from functools import lru_cache

from langchain_openai import OpenAIEmbeddings

from rag_app.core.config import get_settings


@lru_cache(maxsize=1)
def get_embedding_model() -> OpenAIEmbeddings:
    """Get or create OpenAI embeddings model."""
    settings = get_settings()
    
    if not settings.openai_api_key:
        raise ValueError("OPENAI_API_KEY is required for embeddings. Add it to your .env file.")
    
    # Note: Embeddings always use the official OpenAI API endpoint
    # Do not use custom base_url as it may not support embeddings
    return OpenAIEmbeddings(
        api_key=settings.openai_api_key,
        model=settings.embedding_model,
    )


def embed_texts(texts: list[str]) -> list[list[float]]:
    """Embed a list of texts using OpenAI embeddings."""
    if not texts:
        return []
    
    embeddings_model = get_embedding_model()
    vectors = embeddings_model.embed_documents(texts)
    return vectors

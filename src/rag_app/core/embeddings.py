from functools import lru_cache

from langchain_core.embeddings import Embeddings
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_openai import OpenAIEmbeddings

from rag_app.core.config import get_settings


@lru_cache(maxsize=1)
def get_embedding_model() -> Embeddings:
    """Get or create embeddings model based on provider configuration."""
    settings = get_settings()

    provider = settings.embedding_provider.lower()

    if provider == "huggingface":
        # Use token if provided for authenticated downloads
        hf_kwargs = {"model_name": settings.embedding_model}
        if settings.hf_token:
            hf_kwargs["model_kwargs"] = {"token": settings.hf_token}
        return HuggingFaceEmbeddings(**hf_kwargs)

    if provider == "openai":
        if not settings.openai_api_key:
            raise ValueError("OPENAI_API_KEY is required for OpenAI embeddings. Add it to your .env file.")

        return OpenAIEmbeddings(
            api_key=settings.openai_api_key,
            model=settings.embedding_model,
        )

    raise ValueError(
        f"Unsupported EMBEDDING_PROVIDER '{settings.embedding_provider}'. "
        "Use 'huggingface' or 'openai'."
    )


def embed_texts(texts: list[str]) -> list[list[float]]:
    """Embed a list of texts using the configured embedding provider."""
    if not texts:
        return []
    
    embeddings_model = get_embedding_model()
    vectors = embeddings_model.embed_documents(texts)
    return vectors

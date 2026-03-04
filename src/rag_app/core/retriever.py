from typing import Optional
from rag_app.core.config import get_settings
from rag_app.core.vector_store import similarity_search, mmr_search


def is_followup_query(query: str) -> bool:
    """
    Detect if query is likely a follow-up question.
    
    Args:
        query: The current query string
    
    Returns:
        True if query appears to be a follow-up, False otherwise
    """
    followup_keywords = [
        "in detail", "more", "tell me more", "explain", "elaborate",
        "expand", "further", "deeper", "clearer", "example",
        "specifically", "clarify", "what do you mean", "can you",
        "how", "why", "give me an example", "show me"
    ]
    query_lower = query.lower().strip()
    
    # Short queries or queries with follow-up keywords are likely follow-ups
    return len(query_lower.split()) <= 5 and any(
        keyword in query_lower for keyword in followup_keywords
    )


def retrieve(
    query: str,
    top_k: int | None = None,
    use_mmr: bool | None = None,
    previous_query: Optional[str] = None,
    chat_history=None,
) -> list[dict]:
    """
    Retrieve relevant chunks from the vector store.
    
    Args:
        query: Search query string
        top_k: Number of documents to retrieve (uses config default if None)
        use_mmr: Whether to use MMR retrieval (uses config default if None)
        previous_query: Previous user query for context (used in follow-ups)
        chat_history: ChatHistory object to extract context if needed
    
    Returns:
        List of retrieved chunks with metadata
    """
    settings = get_settings()
    k = top_k or settings.top_k
    mmr_enabled = use_mmr if use_mmr is not None else settings.use_mmr
    
    # For follow-up questions, try to combine with previous query for better context
    search_query = query
    if is_followup_query(query):
        if previous_query:
            # Combine current follow-up with previous query
            search_query = f"{previous_query} {query}"
        elif chat_history and len(chat_history.get_all_messages()) >= 2:
            # Extract previous user message from history
            messages = chat_history.get_all_messages()
            for i in range(len(messages) - 1, -1, -1):
                if messages[i].role == "user":
                    prev_msg = messages[i]
                    if i > 0 and messages[i-1].role == "assistant":
                        # Found the previous user message before the last assistant response
                        search_query = f"{prev_msg.content} {query}"
                        break
    
    # Use MMR if enabled, otherwise fall back to similarity search
    if mmr_enabled:
        results = mmr_search(
            query=search_query,
            top_k=k,
            fetch_k=settings.mmr_fetch_k,
            lambda_mult=settings.mmr_lambda_mult,
        )
    else:
        results = similarity_search(query=search_query, top_k=k)
    
    # Format results for consistency
    chunks: list[dict] = []
    for result in results:
        chunks.append({
            "text": result["text"],
            "source": result["source"],
            "chunk_index": result["chunk_index"],
            "similarity_score": result["similarity_score"],
        })
    
    return chunks

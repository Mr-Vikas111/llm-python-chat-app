# LangChain RAG System Migration

This document outlines the changes made to migrate the RAG system to use LangChain with OpenAI embeddings and ChromaDB.

## Overview of Changes

Your RAG system has been refactored to use LangChain components, providing better integration, maintainability, and standardization. The system now uses:

- **LangChain 0.3+** for orchestration and RAG pipelines
- **OpenAI Embeddings** (via `langchain-openai`) for semantic embeddings
- **ChromaDB** (via `langchain-chroma`) for vector storage
- **LangChain Message System** for improved LLM interactions

## Key Changes by Module

### 1. **embeddings.py**
**Before:** Used `sentence-transformers/all-MiniLM-L6-v2` locally
**After:** Uses `OpenAIEmbeddings` with `text-embedding-3-small` model

```python
# Before
from sentence_transformers import SentenceTransformer
model = SentenceTransformer(settings.embedding_model)
vectors = model.encode(texts, normalize_embeddings=True)

# After
from langchain_openai import OpenAIEmbeddings
embeddings = OpenAIEmbeddings(api_key=settings.openai_api_key, model=settings.embedding_model)
vectors = embeddings.embed_documents(texts)
```

**Benefits:**
- Better semantic understanding with OpenAI's latest models
- Seamless integration with LangChain ecosystem
- Automatic API key management

### 2. **vector_store.py**
**Before:** Direct ChromaDB API with manual embedding handling
**After:** LangChain's Chroma wrapper with automatic embeddings

```python
# Before
import chromadb
collection = client.get_or_create_collection(name="collection_name")
collection.upsert(ids=ids, documents=texts, embeddings=vectors, metadatas=metadata)

# After
from langchain_chroma import Chroma
from langchain_core.documents import Document
vector_store = Chroma(
    collection_name="collection_name",
    embedding_function=embeddings,
    persist_directory=str(vector_db_dir),
)
vector_store.add_documents(documents)
```

**Benefits:**
- Automatic embedding computation
- LangChain Document objects with metadata support
- Better separation of concerns
- Simplified API

### 3. **retriever.py**
**Before:** Manual embedding then similarity search
**After:** Direct semantic search with LangChain

```python
# Before
query_vector = embed_texts([query])[0]
result = similarity_search(query_embedding=query_vector, top_k=k)

# After
results = similarity_search(query=query, top_k=k)  # Returns already formatted dicts
```

**Benefits:**
- Cleaner API
- Automatic embedding handling
- Better structured results

### 4. **ingestion/pipeline.py**
**Before:** Separate embedding step
**After:** Integrated embeddings in vector store

```python
# Before
vectors = embed_texts(all_texts)
indexed = upsert_documents(texts=all_texts, embeddings=vectors, metadata=all_meta)

# After
indexed = upsert_documents(texts=all_texts, metadata=all_meta)  # Embeddings automatic
```

**Benefits:**
- Cleaner pipeline
- Fewer moving parts
- Less room for error

### 5. **generator.py**
**Before:** String-based prompts
**After:** LangChain Message system

```python
# Before
prompt = f"{SYSTEM_PROMPT}\n\nContext:\n{context}\n\nQuestion: {question}"
result = chat_model.invoke(prompt)

# After
messages = [
    SystemMessage(content=SYSTEM_PROMPT),
    HumanMessage(content=f"Context:\n{context}\n\nQuestion: {question}")
]
result = chat_model.invoke(messages)
```

**Benefits:**
- Proper message roles and types
- Better LLM understanding of context
- Future-proof for advanced features

### 6. **Configuration Changes**
**Embedding Model:** Changed default from `sentence-transformers/all-MiniLM-L6-v2` to `text-embedding-3-small`

This is a more powerful OpenAI model that provides better semantic understanding.

## Required Environment Variables

Make sure your `.env` file includes:

```env
# Required for OpenAI embeddings
OPENAI_API_KEY=sk-...

# Optional - customize embedding model
EMBEDDING_MODEL=text-embedding-3-small  # Options: text-embedding-3-small, text-embedding-3-large

# Existing variables (still needed)
VECTOR_DB_DIR=data/chroma
COLLECTION_NAME=rag_documents
TOP_K=4
CHUNK_SIZE=800
CHUNK_OVERLAP=120

# For LLM generation (if USE_LLM=true)
USE_LLM=false
LLM_PROVIDER=openai  # or ollama
OPENAI_MODEL=gpt-4o-mini
```

## Installation

With the updated dependencies, reinstall the package:

```bash
pip install -e .
# or with development dependencies:
pip install -e ".[dev]"
```

New dependency: `langchain-chroma>=0.1.0`

## API Response Changes

The `RetrievedChunk` schema has been updated:

```python
# Before
class RetrievedChunk(BaseModel):
    text: str
    source: str
    chunk_index: str
    distance: float | None = None  # Chroma distance metric

# After
class RetrievedChunk(BaseModel):
    text: str
    source: str
    chunk_index: str
    similarity_score: float | None = None  # Semantic similarity score
```

## Vector Database Compatibility

**Important:** The old ChromaDB data created with sentence-transformers embeddings is NOT compatible with the new OpenAI embeddings. 

To start fresh:

```bash
# Backup old data (optional)
mv data/chroma data/chroma_backup

# Remove old vector database
rm -rf data/chroma

# Re-ingest your documents
python scripts/ingest.py
```

This will create a new vector database with OpenAI embeddings.

## Performance Considerations

1. **Embedding Quality:** OpenAI embeddings are significantly more powerful than local models
2. **API Costs:** Each embedding call uses OpenAI API tokens. For production, consider:
   - Batch embedding operations
   - Caching embeddings
   - Using text-embedding-3-small for cost efficiency

3. **Response Time:** LangChain adds minimal overhead while improving code organization

## Testing

Run existing tests to ensure compatibility:

```bash
pytest tests/
```

The test suite includes document chunking tests which remain unchanged.

## Migration Checklist

- [ ] Update `.env` with `OPENAI_API_KEY`
- [ ] Backup existing vector database (optional)
- [ ] Run `pip install -e .` to install new dependencies
- [ ] Delete old vector database if starting fresh: `rm -rf data/chroma`
- [ ] Run `python scripts/ingest.py` to re-ingest documents
- [ ] Test with `python scripts/query_cli.py "your question"`
- [ ] Run `pytest tests/` to verify all tests pass

## Troubleshooting

### ImportError: No module named 'langchain_chroma'
```bash
pip install langchain-chroma
```

### OPENAI_API_KEY Error
Ensure your `.env` file contains a valid OpenAI API key:
```
OPENAI_API_KEY=sk-your-actual-key-here
```

### Vector Store Not Found
Your old ChromaDB is incompatible. Delete it and re-ingest:
```bash
rm -rf data/chroma
python scripts/ingest.py
```

## Benefits Summary

✅ **Better Integration:** LangChain provides unified interfaces across components
✅ **Improved Quality:** OpenAI embeddings provide superior semantic understanding
✅ **Cleaner Code:** Fewer manual steps, more declarative API
✅ **Future-Proof:** Built on industry-standard frameworks
✅ **Better Errors:** More descriptive error messages and validation
✅ **Extensibility:** Easy to add new features (RAG chains, agents, etc.)

## Next Steps

With LangChain, you can now easily add advanced features:

1. **RAG Chains:** Use `langchain.chains.RetrievalQA` for end-to-end RAG
2. **Agents:** Build autonomous agents with tool access
3. **Async Support:** Leverage LangChain's async APIs for better performance
4. **Caching:** Implement semantic caching for embeddings
5. **Multi-Modal:** Extend to handle images, audio, etc.

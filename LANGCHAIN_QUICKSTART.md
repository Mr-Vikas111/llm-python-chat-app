# Quick Start Guide - LangChain RAG System

## Setup

### 1. Install Dependencies
```bash
# Install the package with all dependencies
pip install -e .

# Or with development tools
pip install -e ".[dev]"
```

### 2. Configure Environment
Create a `.env` file in the project root:

```env
# Required: OpenAI API Key
OPENAI_API_KEY=sk-your-key-here

# Optional: Customize models
EMBEDDING_MODEL=text-embedding-3-small
OPENAI_MODEL=gpt-4o-mini
USE_LLM=false  # Set to true to enable LLM answers

# Data directories (defaults shown)
DATA_DIR=data
RAW_DATA_DIR=data/raw
VECTOR_DB_DIR=data/chroma
COLLECTION_NAME=rag_documents

# Query settings
TOP_K=4
CHUNK_SIZE=800
CHUNK_OVERLAP=120
```

### 3. Add Your Documents
Place your documents in `data/raw/`:
- `.txt` files
- `.md` markdown files
- `.pdf` PDF files
- Other supported formats

```bash
# Example
cp your_docs/*.pdf data/raw/
```

## Basic Usage

### Option 1: Command Line
```bash
# Ingest documents
python scripts/ingest.py

# Query the system
python scripts/query_cli.py "What is the main topic?"
python scripts/query_cli.py "Your question here" --top-k 5
```

### Option 2: Streamlit UI
```bash
streamlit run scripts/streamlit_app.py
```

### Option 3: FastAPI Server
```bash
# Start server
python scripts/run_api.py

# Health check
curl http://localhost:8000/health

# Ingest documents
curl -X POST http://localhost:8000/ingest

# Query
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"question": "Your question?", "top_k": 4}'
```

### Option 4: Python Script
```python
from rag_app.core.retriever import retrieve
from rag_app.core.generator import generate_answer

# Retrieve relevant chunks
chunks = retrieve(query="Your question?", top_k=4)

# Generate answer
answer = generate_answer(question="Your question?", chunks=chunks)
print(answer)
```

## Architecture Overview

```
┌─────────────────────────────────────────┐
│         Input Documents (data/raw)      │
└──────────────────┬──────────────────────┘
                   │
                   ▼
        ┌──────────────────────┐
        │  Document Chunking   │
        │  (chunker.py)        │
        └──────────┬───────────┘
                   │
                   ▼
    ┌──────────────────────────────┐
    │  OpenAI Embeddings            │ ◄───── embeddings.py
    │  (LangChain Integration)      │
    └──────────┬───────────────────┘
               │
               ▼
    ┌──────────────────────────────┐
    │  ChromaDB Vector Store        │ ◄───── vector_store.py
    │  (LangChain Integration)      │
    └──────────────────────────────┘
               │
               └─────────────────────────────┐
                                             │
                   Query ──────────────┐     │
                                      ▼     ▼
                            ┌──────────────────────┐
                            │   Similarity Search   │
                            │   (retriever.py)      │
                            └──────────┬────────────┘
                                       │
                        ┌──────────────┴──────────────┐
                        │                             │
                        ▼                             ▼
            ┌─────────────────────┐    ┌──────────────────────┐
            │ Retrieved Chunks    │    │   OpenAI LLM         │
            │ (with scores)       │    │   (ChatOpenAI)       │
            └─────────┬───────────┘    └──────────┬───────────┘
                      │                           │
                      └───────────────┬───────────┘
                                      │
                                      ▼
                          ┌──────────────────────┐
                          │  Generated Answer    │
                          │  (generator.py)      │
                          └──────────────────────┘
```

## LangChain Components Used

### Core Components
- **LangChain 0.3+**: Orchestration and RAG patterns
- **LangChain OpenAI**: Chat models and embeddings
- **LangChain Chroma**: Vector store integration
- **LangChain Core**: Base abstractions (Documents, Messages, etc.)

### Key Classes
- `OpenAIEmbeddings`: Text embeddings via OpenAI API
- `Chroma`: Vector database with persistence
- `ChatOpenAI`: Chat model interface
- `Document`: Standard document representation
- `SystemMessage`/`HumanMessage`: Structured chat messages

## Configuration Details

### Embedding Models
**Default:** `text-embedding-3-small`

Options:
- `text-embedding-3-small` (recommended - good quality/cost)
- `text-embedding-3-large` (better quality, higher cost)

### LLM Providers
**Default:** `openai`

- OpenAI: Requires `OPENAI_API_KEY`
- Ollama: Local model, requires running Ollama service

### Chunking Strategy
- **Size:** 800 tokens (default)
- **Overlap:** 120 tokens (for context preservation)

Adjust in `.env`:
```env
CHUNK_SIZE=800
CHUNK_OVERLAP=120
```

## Common Operations

### Reset Vector Store
```bash
# Backup old data
mv data/chroma data/chroma_backup

# Delete vector store
rm -rf data/chroma

# Re-ingest documents
python scripts/ingest.py
```

### Change Embedding Model
```env
EMBEDDING_MODEL=text-embedding-3-large
```

Then reset the vector store (see above).

### Enable LLM Responses
```env
USE_LLM=true
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4o-mini  # Or your preferred model
```

### Adjust Search Results
```env
TOP_K=6  # Get 6 results instead of 4
```

## Troubleshooting

### API Key Issues
```
ValueError: OPENAI_API_KEY is required
```
Solution: Add `OPENAI_API_KEY=sk-...` to `.env`

### No Documents Found
```
No relevant context found.
```
Solutions:
1. Ensure documents are in `data/raw/`
2. Run `python scripts/ingest.py` to ingest them
3. Try broader search terms

### Module Import Errors
```
ModuleNotFoundError: No module named 'langchain_chroma'
```
Solution:
```bash
pip install langchain-chroma
# Or reinstall everything
pip install -e .
```

### Old Vector Store Issues
If you migrated from the old system:
```bash
# The old ChromaDB is incompatible with OpenAI embeddings
rm -rf data/chroma  # Delete old data
python scripts/ingest.py  # Create new one
```

## Performance Tips

1. **Batch Operations:** Embed multiple texts at once
2. **Caching:** LangChain automatically caches within sessions
3. **Model Selection:** `text-embedding-3-small` is sufficient for most use cases
4. **Top-K Tuning:** Start with `TOP_K=4`, increase if results are poor

## Next Steps

1. Add your documents to `data/raw/`
2. Run `python scripts/ingest.py`
3. Try the Streamlit UI or CLI
4. Explore advanced features in the [LANGCHAIN_MIGRATION.md](LANGCHAIN_MIGRATION.md)

## Resources

- [LangChain Documentation](https://python.langchain.com/)
- [OpenAI API Docs](https://platform.openai.com/docs/)
- [ChromaDB Docs](https://docs.trychroma.com/)
- [Project README](README.md)

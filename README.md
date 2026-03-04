# RAG DB Model

A production-ready starter template for a Retrieval-Augmented Generation (RAG) app using:
- FastAPI for serving
- Streamlit for chat UI
- ChromaDB for vector storage
- Sentence Transformers for embeddings
- LangChain for LLM orchestration
- OpenAI-compatible LLM for answer generation (default)

## Project Structure

- `src/rag_app/core/` → chunking, embeddings, retrieval, generation, config
- `src/rag_app/ingestion/` → document loaders and indexing pipeline
- `src/rag_app/api/` → FastAPI app and schemas
- `scripts/` → local run scripts
- `data/raw/` → your source documents
- `data/chroma/` → persisted vector index

## Quick Start

1. Create and activate environment:
   - `python3 -m venv .venv`
   - `source .venv/bin/activate`
2. Install package:
   - `pip install -e .[dev]`
3. Configure env:
   - `cp .env.example .env`
4. Add documents to `data/raw/` (`.txt`, `.md`, `.rst`, `.pdf`)
5. Ingest documents:
   - `PYTHONPATH=src python scripts/ingest.py`
6. Run API:
   - `PYTHONPATH=src python scripts/run_api.py`
7. Run Streamlit chat UI:
   - `PYTHONPATH=src streamlit run scripts/streamlit_app.py`

## API

- `GET /health`
- `POST /ingest`
- `POST /query`

Example query request:

```json
{
  "question": "What does our return policy say?",
  "top_k": 4
}
```

## OpenAI LLM (Default)

Set in `.env`:
- `USE_LLM=true`
- `LLM_PROVIDER=openai`
- `OPENAI_API_KEY=your_key_here`
- `OPENAI_MODEL=gpt-4o-mini`

Optional custom endpoint:
- `OPENAI_BASE_URL=https://api.openai.com/v1`

## Ollama (Optional)

If you want local inference instead:
- `LLM_PROVIDER=ollama`
- `OLLAMA_MODEL=llama3.2:3b`
- `OLLAMA_BASE_URL=http://localhost:11434`

## Dev Commands

- `make fmt` → format/check with Ruff
- `make test` → run tests
- `make run` → run API
- `make ui` → run Streamlit chat UI

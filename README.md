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

## Embeddings Provider

Set embedding backend in `.env`:
- `EMBEDDING_PROVIDER=huggingface` (recommended default)
- `EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2`

OpenAI embeddings option:
- `EMBEDDING_PROVIDER=openai`
- `EMBEDDING_MODEL=text-embedding-3-small`
- `OPENAI_API_KEY=your_key_here`

## Ollama (Optional)

If you want local inference instead:
- `LLM_PROVIDER=ollama`
- `OLLAMA_MODEL=llama3.2:3b`
- `OLLAMA_BASE_URL=http://localhost:11434`

## Hugging Face (Optional)

If you want local Hugging Face generation instead:
- `LLM_PROVIDER=huggingface`
- `HF_MODEL_ID=TinyLlama/TinyLlama-1.1B-Chat-v1.0`
- `HF_TASK=text-generation`
- `HF_TEMPERATURE=0.5`
- `HF_MAX_NEW_TOKENS=512`
- `HF_TOKEN=your_hf_token_here` (optional but recommended)

This uses LangChain's `HuggingFacePipeline` wrapped by `ChatHuggingFace` for response generation.

**Getting HF Token (Recommended):**
1. Create account at https://huggingface.co/
2. Go to https://huggingface.co/settings/tokens
3. Create a new "Read" token
4. Add it to `.env` as `HF_TOKEN=hf_xxxxxxxxxxxx`

Benefits of using HF_TOKEN:
- Higher rate limits for model downloads
- Faster download speeds
- Access to gated models (if you have permission)
- No unauthenticated request warnings

## Dev Commands

- `make fmt` → format/check with Ruff
- `make test` → run tests
- `make run` → run API
- `make ui` → run Streamlit chat UI

## Streamlit Cloud Deployment Notes

When deploying on Streamlit Cloud, set runtime values in app **Secrets** (Settings → Secrets), for example:

```toml
USE_LLM = "true"
LLM_PROVIDER = "huggingface"
HF_MODEL_ID = "TinyLlama/TinyLlama-1.1B-Chat-v1.0"
HF_TOKEN = "hf_xxx"

EMBEDDING_PROVIDER = "huggingface"
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
```

If `USE_LLM` is not set correctly, the app may return: "LLM disabled (USE_LLM=false)".

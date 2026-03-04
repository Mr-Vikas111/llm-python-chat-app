.PHONY: install ingest run ui query test fmt

install:
	pip install -e .[dev]

ingest:
	PYTHONPATH=src python scripts/ingest.py

run:
	PYTHONPATH=src python scripts/run_api.py

ui:
	PYTHONPATH=src streamlit run scripts/streamlit_app.py

query:
	PYTHONPATH=src python scripts/query_cli.py "What is in the knowledge base?"

test:
	PYTHONPATH=src pytest

fmt:
	ruff check .

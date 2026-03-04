from rag_app.ingestion.pipeline import ingest_from_raw_data


if __name__ == "__main__":
    result = ingest_from_raw_data()
    print(result)

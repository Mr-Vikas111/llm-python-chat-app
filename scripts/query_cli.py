import argparse

from rag_app.core.generator import generate_answer
from rag_app.core.retriever import retrieve


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Query the local RAG index")
    parser.add_argument("question", type=str)
    parser.add_argument("--top-k", type=int, default=None)
    args = parser.parse_args()

    chunks = retrieve(args.question, top_k=args.top_k)
    answer = generate_answer(args.question, chunks)
    print("\n=== ANSWER ===\n")
    print(answer)
    print("\n=== SOURCES ===\n")
    for chunk in chunks:
        print(f"- {chunk['source']} (chunk {chunk['chunk_index']})")

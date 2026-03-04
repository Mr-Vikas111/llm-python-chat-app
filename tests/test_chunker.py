from rag_app.core.chunker import split_text


def test_split_text_creates_chunks() -> None:
    text = " ".join(["token"] * 400)
    chunks = split_text(text=text, source="doc.txt", chunk_size=120, chunk_overlap=20)

    assert len(chunks) > 1
    assert chunks[0].source == "doc.txt"
    assert chunks[0].index == 0

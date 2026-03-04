from dataclasses import dataclass

from langchain_text_splitters import RecursiveCharacterTextSplitter


@dataclass(frozen=True)
class Chunk:
    text: str
    source: str
    index: int


def split_text(text: str, source: str, chunk_size: int, chunk_overlap: int) -> list[Chunk]:
    """
    Split text into chunks using LangChain's RecursiveCharacterTextSplitter.
    
    This splitter first tries to split on natural boundaries:
    1. Paragraphs ("\n\n")
    2. Sentences (".")
    3. Words (" ")
    4. Characters as fallback
    
    This approach preserves semantic meaning better than simple character splitting.
    """
    if not text or not text.strip():
        return []

    if chunk_overlap >= chunk_size:
        raise ValueError("chunk_overlap must be smaller than chunk_size")

    # Initialize the splitter with smart boundaries
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        # Try to split on these boundaries in order (paragraphs, sentences, words, chars)
        separators=["\n\n", "\n", ".", " ", ""],
        length_function=len,
    )

    # Split the text
    split_texts = splitter.split_text(text)

    # Convert to Chunk objects
    chunks: list[Chunk] = []
    for index, chunk_text in enumerate(split_texts):
        chunk_text = chunk_text.strip()
        if chunk_text:  # Skip empty chunks
            chunks.append(Chunk(text=chunk_text, source=source, index=index))

    return chunks

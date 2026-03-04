from pathlib import Path


SUPPORTED_EXTENSIONS = {".txt", ".md", ".markdown", ".rst", ".pdf"}


def _read_pdf(path: Path) -> str:
    try:
        from pypdf import PdfReader
    except ImportError as exc:
        raise RuntimeError("PDF support requires pypdf. Install dependencies first.") from exc

    reader = PdfReader(str(path))
    pages = [page.extract_text() or "" for page in reader.pages]
    return "\n".join(pages).strip()


def read_document(path: Path) -> str:
    ext = path.suffix.lower()
    if ext == ".pdf":
        return _read_pdf(path)
    return path.read_text(encoding="utf-8", errors="ignore").strip()


def collect_documents(root: Path) -> list[tuple[str, str]]:
    docs: list[tuple[str, str]] = []
    if not root.exists():
        return docs

    for path in sorted(root.rglob("*")):
        if not path.is_file() or path.suffix.lower() not in SUPPORTED_EXTENSIONS:
            continue
        content = read_document(path)
        if content:
            docs.append((str(path), content))
    return docs

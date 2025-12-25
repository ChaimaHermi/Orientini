from pathlib import Path


def load_corpus(path: Path) -> list[str]:
    """
    Chaque bloc séparé par ### correspond à UNE formation complète.
    """
    text = path.read_text(encoding="utf-8")

    chunks = []
    for block in text.split("###"):
        block = block.strip()
        if block:
            chunks.append(block)

    return chunks

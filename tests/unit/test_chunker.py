import pytest
from app.domain.retrieval.services.chunker import RecursiveTextChunker


def test_chunker_empty_string() -> None:
    chunker = RecursiveTextChunker(chunk_size=100, chunk_overlap=10)
    assert chunker.split_text("") == []
    assert chunker.split_text("   ") == []


def test_chunker_small_text() -> None:
    chunker = RecursiveTextChunker(chunk_size=100, chunk_overlap=10)
    text = "Paragraph 1 is small.\n\nParagraph 2 is also small."
    chunks = chunker.split_text(text)
    assert len(chunks) == 1
    assert "Paragraph 1" in chunks[0]
    assert "Paragraph 2" in chunks[0]


def test_chunker_splits_large_text() -> None:
    chunker = RecursiveTextChunker(chunk_size=10, chunk_overlap=2)
    text = "Word1 Word2 Word3 Word4 Word5 Word6 Word7 Word8 Word9 Word10 Word11 Word12 Word13 Word14 Word15"
    chunks = chunker.split_text(text)
    assert len(chunks) >= 2

def calculate_recall_at_k(retrieved_docs: list[str], expected_doc: str) -> float:
    return 1.0 if any(expected_doc in doc for doc in retrieved_docs) else 0.0


def calculate_tool_precision(selected_tool: str | None, expected_tool: str) -> float:
    return 1.0 if selected_tool == expected_tool else 0.0


def calculate_citation_precision(citations: list[str], expected_citations: list[str]) -> float:
    if not citations or not expected_citations:
        return 0.0
    matches = sum(1 for c in expected_citations if any(c in cite for cite in citations))
    return matches / len(expected_citations)

from __future__ import annotations


class Retriever:
    def retrieve(self, query: str, top_k: int = 5) -> list[str]:
        raise NotImplementedError("Retrieval is not implemented yet.")

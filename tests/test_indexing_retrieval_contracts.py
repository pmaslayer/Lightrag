from __future__ import annotations

import pytest

from indexing.indexer import Indexer
from retrieval.retriever import Retriever


def test_indexer_contract() -> None:
    with pytest.raises(NotImplementedError):
        Indexer().index([])


def test_retriever_contract() -> None:
    with pytest.raises(NotImplementedError):
        Retriever().retrieve("query", top_k=3)

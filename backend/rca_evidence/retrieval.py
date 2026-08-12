"""Deterministic local BM25 retrieval with citation-ready results."""

from __future__ import annotations

import math
import re
from collections import Counter, defaultdict
from dataclasses import dataclass
from typing import Any, List, Mapping, Sequence


_TOKEN_PATTERN = re.compile(r"[a-z0-9_]+")


def tokenize(text: str) -> List[str]:
    return _TOKEN_PATTERN.findall(text.lower().replace("-", "_"))


@dataclass(frozen=True)
class RetrievalHit:
    document_id: str
    root_cause: str
    score: float
    title: str
    text: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "document_id": self.document_id,
            "root_cause": self.root_cause,
            "score": self.score,
            "title": self.title,
            "text": self.text,
        }


class BM25Index:
    """Small in-memory BM25 index suitable for the versioned benchmark corpus."""

    def __init__(
        self,
        documents: Sequence[Mapping[str, Any]],
        *,
        k1: float = 1.5,
        b: float = 0.75,
    ) -> None:
        if not documents:
            raise ValueError("Knowledge corpus must contain at least one document")
        self._documents = [dict(document) for document in documents]
        self._k1 = k1
        self._b = b
        self._term_frequencies: list[Counter[str]] = []
        self._document_lengths: list[int] = []
        document_frequency: defaultdict[str, int] = defaultdict(int)

        for document in self._documents:
            required = {"document_id", "root_cause", "title", "text"}
            missing = required.difference(document)
            if missing:
                raise ValueError(f"Corpus document missing fields: {sorted(missing)}")
            tokens = tokenize(f"{document['title']} {document['text']}")
            frequencies = Counter(tokens)
            self._term_frequencies.append(frequencies)
            self._document_lengths.append(len(tokens))
            for token in frequencies:
                document_frequency[token] += 1

        self._average_length = sum(self._document_lengths) / len(
            self._document_lengths
        )
        document_count = len(self._documents)
        self._inverse_document_frequency = {
            token: math.log(
                1.0 + (document_count - frequency + 0.5) / (frequency + 0.5)
            )
            for token, frequency in document_frequency.items()
        }

    def search(self, query: str, *, limit: int = 5) -> List[RetrievalHit]:
        if limit <= 0:
            raise ValueError("Retrieval limit must be positive")
        query_tokens = tokenize(query)
        if not query_tokens:
            return []

        scored: list[RetrievalHit] = []
        for document, frequencies, document_length in zip(
            self._documents,
            self._term_frequencies,
            self._document_lengths,
        ):
            score = 0.0
            for token in query_tokens:
                term_frequency = frequencies.get(token, 0)
                if term_frequency == 0:
                    continue
                inverse_frequency = self._inverse_document_frequency.get(token, 0.0)
                denominator = term_frequency + self._k1 * (
                    1.0
                    - self._b
                    + self._b * document_length / self._average_length
                )
                score += inverse_frequency * (
                    term_frequency * (self._k1 + 1.0) / denominator
                )
            if score > 0.0:
                scored.append(
                    RetrievalHit(
                        document_id=str(document["document_id"]),
                        root_cause=str(document["root_cause"]),
                        score=score,
                        title=str(document["title"]),
                        text=str(document["text"]),
                    )
                )

        return sorted(
            scored,
            key=lambda hit: (-hit.score, hit.document_id),
        )[:limit]

    @property
    def document_count(self) -> int:
        return len(self._documents)

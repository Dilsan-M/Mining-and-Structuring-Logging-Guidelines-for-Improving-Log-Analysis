"""Retrieval and answer generation over the logging-guideline collection."""
from dataclasses import dataclass, field
from typing import Iterator

import chromadb
import ollama

import config

SYSTEM_PROMPT = """You are a logging-practices assistant grounded in a catalogue of \
logging guidelines, worked examples, theme definitions and academic literature.

Answer using ONLY the numbered context items.

Rules:
- Give the final answer only. Never narrate how you evaluated the items.
- Write 3-6 sentences, or a short bullet list, and always state the rule in your
  own words rather than replying with a bare citation.
- Cite the items you rely on by number, e.g. [2].
- If the context does not answer the question, say so instead of inventing rules.
- Be concrete and concise.
"""

_collection = None


def get_collection():
    global _collection
    if _collection is None:
        client = chromadb.PersistentClient(path=str(config.CHROMA_PATH))
        _collection = client.get_collection(config.COLLECTION_NAME)
    return _collection


@dataclass
class Hit:
    document: str
    metadata: dict = field(default_factory=dict)
    distance: float = 0.0

    @property
    def title(self) -> str:
        first = self.document.splitlines()[0]
        for prefix in ("Guideline: ", "Theme definition: ", "Academic publication: ",
                       "Example for guideline: "):
            if first.startswith(prefix):
                return first[len(prefix):].strip()
        return first.strip()

    @property
    def source(self) -> str:
        meta = self.metadata
        label = (
            meta.get("consolidated_id")
            or meta.get("example_id")
            or meta.get("theme")
            or meta.get("url")
            or meta.get("source_file")
            or "catalogue"
        )
        return f"{meta.get('doc_type', 'item')}:{label}"


def _build_where(doc_type: str | None, theme: str | None, dimension: str | None):
    clauses = []
    if doc_type:
        clauses.append({"doc_type": doc_type})
    if theme:
        clauses.append({"theme": theme})
    if dimension:
        clauses.append({"dimension": dimension})
    if not clauses:
        return None
    return clauses[0] if len(clauses) == 1 else {"$and": clauses}


def search(
    question: str,
    n_results: int = config.DEFAULT_N_RESULTS,
    doc_type: str | None = None,
    theme: str | None = None,
    dimension: str | None = None,
) -> list[Hit]:
    result = get_collection().query(
        query_texts=[question],
        n_results=n_results,
        where=_build_where(doc_type, theme, dimension),
    )
    if not result["ids"][0]:
        return []
    return [
        Hit(document=d, metadata=m or {}, distance=dist)
        for d, m, dist in zip(
            result["documents"][0],
            result["metadatas"][0],
            result["distances"][0],
        )
    ]


def build_context(hits: list[Hit]) -> str:
    blocks = []
    for index, hit in enumerate(hits, start=1):
        blocks.append(f"[{index}] {hit.document}\nSource: {hit.source}")
    return "\n\n".join(blocks)


def _messages(question: str, hits: list[Hit]) -> list[dict]:
    return [
        {"role": "system", "content": SYSTEM_PROMPT},
        {
            "role": "user",
            "content": f"Context items:\n\n{build_context(hits)}\n\nQuestion: {question}",
        },
    ]


def stream_answer(question: str, hits: list[Hit]) -> Iterator[str]:
    """Yield answer text only; Qwen3's reasoning stays in the separate think channel."""
    stream = ollama.chat(
        model=config.OLLAMA_MODEL,
        messages=_messages(question, hits),
        stream=True,
        think=config.OLLAMA_THINK,
        options=config.OLLAMA_OPTIONS,
    )
    for chunk in stream:
        text = chunk["message"].get("content")
        if text:
            yield text


def generate_answer(question: str, hits: list[Hit]) -> str:
    response = ollama.chat(
        model=config.OLLAMA_MODEL,
        messages=_messages(question, hits),
        think=config.OLLAMA_THINK,
        options=config.OLLAMA_OPTIONS,
    )
    return response["message"]["content"].strip()

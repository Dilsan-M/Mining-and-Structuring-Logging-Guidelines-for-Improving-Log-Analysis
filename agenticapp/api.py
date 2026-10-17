"""FastAPI service exposing retrieval and RAG chat over the logging guidelines."""
import json
from typing import Iterator, Literal

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

import config
import rag

app = FastAPI(
    title="Logging Guidelines RAG",
    description="Retrieval-augmented chat over the logging guideline catalogue.",
    version="1.0.0",
)

STATIC_DIR = config.PROJECT_ROOT / "static"
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

DocType = Literal["guideline", "example", "theme", "literature", "occurrence"]


class SearchRequest(BaseModel):
    query: str = Field(min_length=1)
    n_results: int = Field(default=config.DEFAULT_N_RESULTS, ge=1, le=50)
    doc_type: DocType | None = None
    theme: str | None = None
    dimension: str | None = None


class ChatRequest(SearchRequest):
    stream: bool = False


class HitModel(BaseModel):
    rank: int
    title: str
    document: str
    source: str
    distance: float
    metadata: dict


class RelatedResponse(BaseModel):
    consolidated_id: str
    guideline: str | None
    guideline_repository: str | None = None
    guideline_source_file: str | None = None
    guideline_url: str | None = None
    references: list[dict] = []
    examples: list[dict]


def _repo_to_github_url(repo_name: str | None) -> str | None:
    if not repo_name:
        return None
    name = repo_name.strip()
    if not name or "/" not in name:
        return None
    return f"https://github.com/{name}"


def _split_repositories(raw: str | None) -> list[str]:
    if not raw:
        return []
    # Consolidated rows store multi-source provenance as ';' separated repo names.
    return [part.strip() for part in raw.split(";") if part.strip()]


def _extract_example_content(document: str) -> str:
    lines = document.splitlines()
    try:
        start = next(index for index, line in enumerate(lines) if line.startswith("Example content:"))
    except StopIteration:
        return ""

    content = []
    for line in lines[start + 1:]:
        if line.startswith("Theme:") or line.startswith("Repository:"):
            break
        content.append(line)
    return "\n".join(content).strip()


class SearchResponse(BaseModel):
    query: str
    hits: list[HitModel]


class ChatResponse(BaseModel):
    query: str
    answer: str
    sources: list[HitModel]


def _to_models(hits: list[rag.Hit]) -> list[HitModel]:
    return [
        HitModel(
            rank=index,
            title=hit.title,
            document=hit.document,
            source=hit.source,
            distance=hit.distance,
            metadata=hit.metadata,
        )
        for index, hit in enumerate(hits, start=1)
    ]


def _retrieve(request: SearchRequest) -> list[rag.Hit]:
    hits = rag.search(
        request.query,
        n_results=request.n_results,
        doc_type=request.doc_type,
        theme=request.theme,
        dimension=request.dimension,
    )
    if not hits:
        raise HTTPException(status_code=404, detail="No matching documents found.")
    return hits


@app.get("/", include_in_schema=False)
def index() -> FileResponse:
    return FileResponse(STATIC_DIR / "index.html")


@app.get("/health")
def health() -> dict:
    try:
        count = rag.get_collection().count()
    except Exception as exc:
        raise HTTPException(status_code=503, detail=f"Collection unavailable: {exc}") from exc
    return {"status": "ok", "documents": count, "model": config.OLLAMA_MODEL}


@app.get("/themes")
def themes() -> dict:
    result = rag.get_collection().get(where={"doc_type": "theme"}, include=["metadatas"])
    entries = [
        {
            "theme": m.get("theme"),
            "dimension": m.get("dimension"),
            "basis": m.get("theme_basis"),
        }
        for m in result["metadatas"]
    ]
    entries.sort(key=lambda e: (e["dimension"] or "", e["theme"] or ""))
    return {"count": len(entries), "themes": entries}


@app.get("/related/{consolidated_id}", response_model=RelatedResponse)
def related(consolidated_id: str) -> RelatedResponse:
    collection = rag.get_collection()

    guideline_result = collection.get(
        where={
            "$and": [
                {"doc_type": "guideline"},
                {"consolidated_id": consolidated_id},
            ]
        },
        include=["documents", "metadatas"],
    )
    guideline_text = None
    guideline_repository = None
    guideline_source_file = None
    guideline_url = None
    if guideline_result["documents"]:
        first_line = guideline_result["documents"][0].splitlines()[0]
        guideline_text = first_line.removeprefix("Guideline: ").strip()
        first_meta = guideline_result["metadatas"][0] or {}
        guideline_repository = first_meta.get("repositories")
        guideline_source_file = first_meta.get("source_file")
        guideline_url = first_meta.get("url")

    example_result = collection.get(
        where={
            "$and": [
                {"doc_type": "example"},
                {"consolidated_id": consolidated_id},
            ]
        },
        include=["documents", "metadatas"],
    )
    examples = []
    reference_seen = set()
    references = []

    for repo in _split_repositories(guideline_repository):
        ref = {
            "repository": repo,
            "source_file": None,
            "url": _repo_to_github_url(repo),
            "kind": "repository",
        }
        dedupe_key = (ref["repository"], ref["source_file"], ref["url"], ref["kind"])
        if dedupe_key not in reference_seen:
            reference_seen.add(dedupe_key)
            references.append(ref)

    for doc, meta in zip(example_result["documents"], example_result["metadatas"]):
        snippet = _extract_example_content(doc)
        examples.append(
            {
                "example_id": meta.get("example_id"),
                "repository": meta.get("repositories"),
                "source_file": meta.get("source_file"),
                "url": meta.get("url"),
                "code_involved": meta.get("code_involved"),
                "snippet": snippet,
            }
        )

        ref = {
            "repository": meta.get("repositories"),
            "source_file": meta.get("source_file"),
            "url": meta.get("url"),
            "kind": "example",
        }
        dedupe_key = (ref["repository"], ref["source_file"], ref["url"], ref["kind"])
        if dedupe_key not in reference_seen:
            reference_seen.add(dedupe_key)
            references.append(ref)

    return RelatedResponse(
        consolidated_id=consolidated_id,
        guideline=guideline_text,
        guideline_repository=guideline_repository,
        guideline_source_file=guideline_source_file,
        guideline_url=guideline_url,
        references=references,
        examples=examples,
    )


@app.post("/search", response_model=SearchResponse)
def search(request: SearchRequest) -> SearchResponse:
    return SearchResponse(query=request.query, hits=_to_models(_retrieve(request)))


def _ndjson_events(query: str, hits: list[rag.Hit]) -> Iterator[str]:
    """Tokens arrive first for textual answer-first UX; sources follow."""
    for text in rag.stream_answer(query, hits):
        yield json.dumps({"type": "token", "text": text}) + "\n"
    payload = [m.model_dump() for m in _to_models(hits)]
    yield json.dumps({"type": "sources", "sources": payload}) + "\n"
    yield json.dumps({"type": "done"}) + "\n"


@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    hits = _retrieve(request)
    if request.stream:
        return StreamingResponse(
            _ndjson_events(request.query, hits),
            media_type="application/x-ndjson",
        )
    return ChatResponse(
        query=request.query,
        answer=rag.generate_answer(request.query, hits),
        sources=_to_models(hits),
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host=config.API_HOST, port=config.API_PORT)

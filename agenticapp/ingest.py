"""Build the ChromaDB collection from the logging-guideline workbooks.

Sources:
  5.Final Result.xlsx   consolidated catalogue, examples, codebook, academic coverage
  1.LiteraturePhase1.1  literature screening table
  4.9...VALIDATION      raw source-level occurrences (optional, superseded)
"""
import argparse
import hashlib

import chromadb
import pandas as pd

import config


def clean(value) -> str | None:
    if value is None or pd.isna(value):
        return None
    text = str(value).strip()
    return text or None


def add_field(parts: list[str], label: str, value) -> None:
    text = clean(value)
    if text:
        parts.append(f"{label}: {text}")


def meta_from(row, columns: dict[str, str]) -> dict:
    out = {}
    for source_column, key in columns.items():
        value = clean(row.get(source_column))
        if value is not None:
            out[key] = value[:600]
    return out


def load_consolidated(path) -> list[tuple[str, str, dict]]:
    df = pd.read_excel(path, "Consolidated Guideline")
    records = []
    for _, row in df.iterrows():
        guideline = clean(row.get("Consolidated Guideline"))
        if not guideline:
            continue
        parts = [f"Guideline: {guideline}"]
        add_field(parts, "Dimension", row.get("Type(s)"))
        add_field(parts, "Theme", row.get("Updated Theme(s)"))
        add_field(parts, "Theme basis", row.get("Theme Basis(es)"))
        add_field(parts, "Wording variants", row.get("Original Guideline Variants"))
        add_field(parts, "Repositories", row.get("Repositories"))
        metadata = {"doc_type": "guideline"}
        metadata.update(
            meta_from(
                row,
                {
                    "Consolidated ID": "consolidated_id",
                    "Type(s)": "dimension",
                    "Updated Theme(s)": "theme",
                    "Theme Basis(es)": "theme_basis",
                    "Consolidation Kind": "consolidation_kind",
                    "Repositories": "repositories",
                },
            )
        )
        for column, key in (
            ("Source Occurrence Count", "occurrences"),
            ("Distinct Repository Count", "repository_count"),
            ("Example Reason Count", "example_count"),
        ):
            value = row.get(column)
            if pd.notna(value):
                metadata[key] = int(value)
        records.append((guideline, "\n".join(parts), metadata))
    return records


def try_load(loader, *args) -> list[tuple[str, str, dict]]:
    try:
        return loader(*args)
    except Exception:
        return []


def load_examples(path) -> list[tuple[str, str, dict]]:
    df = pd.read_excel(path, "Example Sheet")
    records = []
    for _, row in df.iterrows():
        example = clean(row.get("Example Reason (original Content)"))
        guideline = clean(row.get("Consolidated Guideline"))
        if not example or not guideline:
            continue
        parts = [f"Example for guideline: {guideline}", f"Example content:\n{example}"]
        add_field(parts, "Theme", row.get("Theme(s)"))
        add_field(parts, "Repository", row.get("Repository"))
        metadata = {"doc_type": "example"}
        metadata.update(
            meta_from(
                row,
                {
                    "Example Reason ID": "example_id",
                    "Consolidated ID": "consolidated_id",
                    "Type(s)": "dimension",
                    "Theme(s)": "theme",
                    "Source File": "source_file",
                    "Repository": "repositories",
                    "Link/URL": "url",
                    "Code Involved": "code_involved",
                },
            )
        )
        records.append((f"example::{example}::{guideline}", "\n".join(parts), metadata))
    return records


def load_codebook(path) -> list[tuple[str, str, dict]]:
    df = pd.read_excel(path, "Codebook")
    records = []
    for _, row in df.iterrows():
        theme = clean(row.get("Theme"))
        if not theme:
            continue
        parts = [f"Theme definition: {theme}"]
        add_field(parts, "Dimension", row.get("Type"))
        add_field(parts, "Basis", row.get("Theme Basis"))
        add_field(parts, "Definition", row.get("Definition / Scope"))
        metadata = {"doc_type": "theme"}
        metadata.update(
            meta_from(
                row,
                {
                    "Type": "dimension",
                    "Theme": "theme",
                    "Theme Basis": "theme_basis",
                    "Codebook Status": "codebook_status",
                },
            )
        )
        records.append((f"theme::{theme}", "\n".join(parts), metadata))
    return records


LITERATURE_DIMENSIONS = {
    "What To Log": "What to log",
    "what to log": "What to log",
    "Where To Log": "Where to log",
    "where to log": "Where to log",
    "How To Log": "How to log",
    "how to log": "How to log",
    "Log Verbosity": "Log levels and verbosity",
    "log verbosility": "Log levels and verbosity",
}


def load_literature(path, sheet: str, tag: str) -> list[tuple[str, str, dict]]:
    df = pd.read_excel(path, sheet)
    records = []
    for _, row in df.iterrows():
        title = clean(row.get("Literature"))
        if not title:
            continue
        parts = [f"Academic publication: {title}"]
        for column, label in LITERATURE_DIMENSIONS.items():
            if column in df.columns:
                add_field(parts, label, row.get(column))
        for column in ("Guidelines", "Comment/Notes"):
            if column in df.columns:
                add_field(parts, column, row.get(column))
        if len(parts) == 1:
            continue
        metadata = {"doc_type": "literature", "source_table": tag}
        for column, key in (("Link/URL", "url"), ("Year", "year"), ("year", "year")):
            value = clean(row.get(column))
            if value:
                metadata[key] = value
        records.append((f"lit::{tag}::{title}", "\n".join(parts), metadata))
    return records


def load_occurrences(path) -> list[tuple[str, str, dict]]:
    workbook = pd.ExcelFile(path)
    records = []
    for sheet in ("Logging Guidelines", "Inductive Review"):
        if sheet not in workbook.sheet_names:
            continue
        df = workbook.parse(sheet)
        df = df.loc[:, [c for c in df.columns if not c.endswith(".1")]]
        for position, row in df.iterrows():
            guideline = clean(row.get("Guideline"))
            if not guideline or guideline.upper() == "NO_GUIDELINE":
                continue
            parts = [f"Guideline: {guideline}"]
            add_field(parts, "Theme", row.get("Theme"))
            add_field(parts, "Dimension", row.get("Type"))
            add_field(parts, "Keywords", row.get("Content Tag"))
            content = clean(row.get("Content"))
            if content and content != guideline:
                parts.append(f"Original excerpt: {content}")
            metadata = {"doc_type": "occurrence", "sheet": sheet, "row": int(position) + 2}
            metadata.update(
                meta_from(
                    row,
                    {
                        "Theme": "theme",
                        "Type": "dimension",
                        "Source File": "source_file",
                        "Repository name": "repositories",
                        "Link/URL": "url",
                        "Language": "language",
                    },
                )
            )
            records.append((f"occ::{sheet}::{guideline}", "\n".join(parts), metadata))
    return records


def collect(include_occurrences: bool) -> list[tuple[str, str, dict]]:
    records = []
    # Priority order: 5 (final) -> 4.8 (earlier consolidated) -> literature -> optional 4.9 occurrences.
    records += load_consolidated(config.FINAL_RESULT_XLSX)
    records += load_examples(config.FINAL_RESULT_XLSX)
    records += load_codebook(config.FINAL_RESULT_XLSX)
    records += load_literature(config.FINAL_RESULT_XLSX, "Academic Coverage", "final")
    records += try_load(load_consolidated, config.CONSOLIDATED_48_XLSX)
    records += try_load(load_examples, config.CONSOLIDATED_48_XLSX)
    records += try_load(load_codebook, config.CONSOLIDATED_48_XLSX)
    records += try_load(load_literature, config.CONSOLIDATED_48_XLSX, "Academic Coverage", "v48")
    records += load_literature(config.LITERATURE_XLSX, "Sheet1", "phase1")
    if include_occurrences:
        records += load_occurrences(config.OCCURRENCES_XLSX)

    # Identical wording across sheets previously produced duplicate retrieval hits.
    seen: set[str] = set()
    deduped = []
    for dedupe_key, document, metadata in records:
        digest = hashlib.sha1(" ".join(dedupe_key.lower().split()).encode()).hexdigest()
        if digest in seen:
            continue
        seen.add(digest)
        deduped.append((digest[:16], document, metadata))
    return deduped


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--reset", action="store_true")
    parser.add_argument(
        "--include-occurrences",
        action="store_true",
        help="Also index the raw source-level rows from the 4.9 workbook.",
    )
    parser.add_argument("--batch-size", type=int, default=200)
    args = parser.parse_args()

    records = collect(args.include_occurrences)
    counts: dict[str, int] = {}
    for _, _, metadata in records:
        counts[metadata["doc_type"]] = counts.get(metadata["doc_type"], 0) + 1
    summary = ", ".join(f"{k}={v}" for k, v in sorted(counts.items()))
    print(f"Prepared {len(records)} documents: {summary}")

    client = chromadb.PersistentClient(path=str(config.CHROMA_PATH))
    if args.reset:
        try:
            client.delete_collection(config.COLLECTION_NAME)
            print(f"Deleted existing collection '{config.COLLECTION_NAME}'")
        except Exception:
            pass

    collection = client.get_or_create_collection(
        name=config.COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"},
    )

    for start in range(0, len(records), args.batch_size):
        batch = records[start : start + args.batch_size]
        collection.upsert(
            ids=[r[0] for r in batch],
            documents=[r[1] for r in batch],
            metadatas=[r[2] for r in batch],
        )
        print(f"  embedded {min(start + len(batch), len(records))}/{len(records)}")

    print(f"Done. Collection holds {collection.count()} documents at {config.CHROMA_PATH}")


if __name__ == "__main__":
    main()

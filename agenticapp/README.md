# Agentic Logging Guidelines Assistant

A local search and question-answering app for the logging-guideline catalogue. FastAPI serves the browser UI and API, ChromaDB stores a locally built search index, and Ollama generates answers on the user's machine.

## Requirements

- Python 3.10 or newer
- [Ollama](https://ollama.com/download) installed and running
- The catalogue workbooks listed below; they are not included in this repository

No API key is required. The default model is `gemma3:1b`. Ollama runs it locally; change the model with the `OLLAMA_MODEL` environment variable.

## Install

Run these commands from the `agenticapp` directory.

### Windows PowerShell

```powershell
py -3 -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
ollama pull gemma3:1b
```

### macOS or Linux

```bash
python3 -m venv .venv
.venv/bin/python -m pip install --upgrade pip
.venv/bin/python -m pip install -r requirements.txt
ollama pull gemma3:1b
```

## Add the catalogue data

Create `agenticapp/data/` and place these two workbooks there:

- `5.Final Result.xlsx`
- `1.LiteraturePhase1.1.xlsx`

The earlier consolidated workbook is optional. The raw occurrence workbook is also optional and is only read when you explicitly pass `--include-occurrences`:

- `4.8.logging_guidelines_consolidated_with_codebook_corrected_VALIDATION.xlsx`
- `4.9.logging_guidelines_with_themes_and_inductive_review_VALIDATION_VALIDATION.xlsx`

Keep the workbooks out of Git unless you have confirmed that they are appropriate to redistribute. To store them elsewhere, set `LOGGING_GUIDELINES_DATA_DIR` to their directory before running the commands. These files are inputs, not secrets; credentials and private tokens should never be placed in the data folder or committed.

## Build the local search index

```powershell
# Windows PowerShell
.\.venv\Scripts\python.exe ingest.py --reset
```

```bash
# macOS or Linux
.venv/bin/python ingest.py --reset
```

ChromaDB creates `chroma_db/` locally. It is generated output and is ignored by Git. To also index raw source-level occurrences, append `--include-occurrences` after placing the optional occurrence workbook in the data directory.

## Start the app

Start Ollama, then run from `agenticapp`:

```powershell
# Windows PowerShell
.\.venv\Scripts\python.exe -m uvicorn api:app --reload
```

```bash
# macOS or Linux
.venv/bin/python -m uvicorn api:app --reload
```

Open <http://127.0.0.1:8000/> for the chat interface or <http://127.0.0.1:8000/docs> for the API documentation. The `/health` endpoint reports whether the local index is available.

## Data and privacy

The workbook inputs, vector index, and Ollama model are local and are not tracked by Git. The app does not need cloud credentials. Search and answer generation use the local index and Ollama service; do not expose the API to an untrusted network without adding authentication and deployment protections.
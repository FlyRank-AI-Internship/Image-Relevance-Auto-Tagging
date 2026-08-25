# FlyRank Capstone — AI Image Relevance

AI Image Understanding & Content Matching Engine.

The system processes an image library, extracts structured metadata with a vision model, creates semantic embeddings, ranks images against article content, and applies a mismatch guard before returning a recommendation.

## Core behavior

- A red-fox article should rank a red-fox image first.
- Similar but wrong candidates such as a wolf should be rejected.
- If no candidate is good enough, return `no confident match` instead of guessing.
- Every vision response is schema-validated.
- Low-confidence classifications are flagged.
- AI calls are tracked for cost.
- Human reviewers can approve or reject suggestions.

## Planned stack

- Python 3.11+
- FastAPI
- PostgreSQL
- Pydantic
- Gemini Flash for image understanding
- Gemini embeddings
- SQLAlchemy + Alembic
- Pytest

## Architecture

```text
Images
  |
  v
Batch Job
  |
  v
Vision Model
  |
  v
Validated metadata --------> Image embeddings
                                  |
Posts ---> Post embeddings -------+
                                  |
                                  v
                         Similarity ranking
                                  |
                                  v
                          Mismatch guard
                           /           \
                          v             v
                  Suggested image   No confident match
                          |
                          v
                    Review API
```

## Repository status

Phase 1 — Design and project scaffold.

## Run

```bash
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS/Linux:
# source .venv/bin/activate

pip install -r requirements.txt
uvicorn app.main:app --reload
```

Then open:

- `GET /health`

## Test

```bash
pytest
```

## Seed

Phase 1 placeholder:

```bash
python scripts_seed.py
```

## Limitations

The AI pipeline, database persistence, embeddings, mismatch thresholds, batch jobs, evaluation dataset, and review workflow are not yet implemented. This repository currently contains the Phase 1 design and runnable API scaffold.

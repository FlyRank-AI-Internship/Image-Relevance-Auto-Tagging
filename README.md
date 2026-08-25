# FlyRank Capstone — AI Image Relevance

AI Image Understanding & Content Matching Engine.

This project processes an image library, extracts structured metadata using a vision model, generates semantic embeddings, ranks images against article content, and applies deterministic mismatch guards before returning a recommendation.

The system is designed to prefer safe rejection over confidently returning the wrong image.

## Core Behavior

- A red-fox article ranks a relevant red-fox image first.
- Similar but incorrect candidates such as a wolf are rejected.
- If no suitable candidate passes the safety checks, the API returns `no_confident_match`.
- Vision responses are validated against a Pydantic schema.
- Low-confidence classifications are flagged for review.
- Vision and embedding calls are logged for usage and cost tracking.
- Images and posts are persisted in PostgreSQL.
- Batch image processing supports retries and background execution.
- Human review decisions can be stored through the Review API.
- Retrieval quality is measured using a labeled evaluation set.

## Tech Stack

- Python 3.11+
- FastAPI
- PostgreSQL (Neon)
- SQLAlchemy
- Alembic
- Pydantic
- Gemini Flash for image understanding
- Gemini embeddings
- Pytest

## Architecture

```text
Images
   |
   v
Background Batch Job
   |
   v
Vision Model
   |
   v
Schema-Validated Metadata
   |
   +---------------------> Image Embeddings
                                  |
Posts --------------------> Post Embeddings
                                  |
                                  v
                         Similarity Ranking
                                  |
                                  v
                          Mismatch Guard
                           /          \
                          v            v
                  Suggested Image   No Confident Match
                          |
                          v
                     Review API
```

## Safety Layer

Semantic similarity is used to rank candidates, but similarity alone does not determine whether an image is safe to recommend.

Each candidate is checked using deterministic rules including:

- subject compatibility
- category compatibility
- vision confidence
- similarity threshold

This is important because semantically related but incorrect images can still receive relatively high similarity scores.

For example, during testing a wolf candidate for a red-fox article received:

```text
similarity_score: 0.7684449545382578
accepted: false
reason: Subject mismatch: expected red fox, detected wolf.
```

The correct red-fox image was selected with:

```text
similarity_score: 0.8558015704951459
accepted: true
```

If every candidate fails the guard, the system returns:

```text
status: no_confident_match
selected: null
```

rather than guessing.

## Evaluation

The matching pipeline was evaluated using a labeled set of 10 article-image cases.

### Measured Result

```text
Total cases: 10
Correct Top-1 results: 10
Top-1 precision: 1.0 (100%)
```

The evaluation included examples covering:

- red fox
- wolf
- dog / Golden Retriever
- cattle
- lion

The initial five-case evaluation achieved 80% because `Golden Retriever` was not recognized as a valid subtype of `dog`.

The subject-normalization logic was updated with explicit aliases and the evaluation set was expanded to 10 cases.

The final measured result was 100% Top-1 precision on this small labeled evaluation set.

This result should not be interpreted as 100% accuracy on unseen categories or production-scale datasets.

## API Endpoints

Core endpoints include:

```text
GET  /health

POST /images/analyze
POST /images/process-batch

GET  /jobs/{job_id}

POST /posts
GET  /posts/{post_id}
GET  /posts/{post_id}/images

POST /reviews
GET  /reviews

GET  /ai-costs

POST /eval/run
```

Interactive API documentation is available through FastAPI Swagger UI at:

```text
http://127.0.0.1:8000/docs
```

when the application is running locally.

## Database

The application uses PostgreSQL hosted on Neon.

Database schema changes are managed through Alembic migrations.

Current persisted data includes:

- images and extracted metadata
- image embeddings
- posts
- review decisions

Apply migrations with:

```bash
alembic upgrade head
```

Database credentials are loaded through environment variables and are not committed to the repository.

## Setup

Create a virtual environment:

```bash
python -m venv .venv
```

### Windows

```bash
.venv\Scripts\activate
```

### macOS / Linux

```bash
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Create `.env` from `.env.example` and configure the required environment variables.

Do not commit real API keys or database credentials.

Apply database migrations:

```bash
alembic upgrade head
```

Start the API:

```bash
uvicorn app.main:app --reload
```

Open:

```text
http://127.0.0.1:8000/docs
```

Health check:

```text
GET /health
```

Expected response:

```json
{
  "status": "ok"
}
```

## Tests

Run:

```bash
pytest
```

Latest verified local result:

```text
15 passed, 2 warnings
```

The current automated test suite covers core behaviors including:

- health endpoint
- structured metadata validation
- low-confidence handling
- AI cost-log isolation
- cosine similarity
- mismatch guard behavior
- wolf-on-fox rejection
- review schema validation

## Example Matching Result

For a post about red foxes:

```text
GET /posts/1/images
```

the system returned:

```text
status: matched
selected subject: red fox
similarity_score: 0.8558015704951459
guard accepted: true
```

A wolf candidate in the same ranked result was rejected:

```text
subject: wolf
similarity_score: 0.7684449545382578
accepted: false
reason: Subject mismatch: expected red fox, detected wolf.
```

This demonstrates the intended separation between semantic retrieval and deterministic safety validation.

## AI Usage Tracking

AI calls are logged with information such as:

```text
call_type
provider
model
entity_type
entity_id
input_units
output_units
estimated_cost
created_at
```

Example vision usage recorded during testing:

```text
provider: gemini
model: gemini-3.6-flash
input_units: 1163
output_units: 70
```

Cost estimation is tracked separately from token usage and can remain zero where an exact provider price has not been configured.

## Human Review

Review decisions can be persisted through the Review API.

Supported decisions include:

```text
approved
rejected
```

This creates an explicit human-in-the-loop layer instead of treating every automatic recommendation as final.

## Evidence

Implementation evidence is maintained in:

```text
EVIDENCE.md
```

The file contains proof for major Definition-of-Done requirements, including:

- structured vision output
- confidence handling
- AI usage tracking
- semantic ranking
- mismatch rejection
- no-confident-match behavior
- database migrations
- automated tests
- labeled evaluation results

Development decisions, AI assistance, corrections, and limitations are documented in:

```text
BUILDLOG.md
```

## Limitations

- The current labeled evaluation set contains only 10 cases and focuses on seeded categories.
- The measured 100% Top-1 precision should not be generalized to unseen categories.
- Subject aliases currently cover a limited set of known relationships.
- The current background-job mechanism is suitable for capstone-scale workloads; a larger production system should use a durable queue and worker architecture.
- Embeddings are stored directly in PostgreSQL for the current small dataset. A larger library would benefit from vector indexing such as pgvector.
- Estimated AI cost remains dependent on configured provider pricing.

## Repository Status

Core capstone pipeline implemented and locally verified:

```text
Image ingestion
      ↓
Vision metadata extraction
      ↓
Schema validation
      ↓
Embedding generation
      ↓
PostgreSQL persistence
      ↓
Semantic ranking
      ↓
Mismatch guard
      ↓
Safe recommendation / rejection
      ↓
Human review
      ↓
Evaluation
```

Latest verified automated test result:

```text
15 passed
```

Latest measured evaluation result:

```text
Top-1 precision: 100% (10/10)
```
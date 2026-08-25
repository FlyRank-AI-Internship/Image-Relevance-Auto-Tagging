# BUILDLOG

## Phase 1 — Project Setup

### AI Assistance

AI was used to help translate the capstone requirements into:

- the initial FastAPI backend structure
- the one-page design document
- Pydantic schemas
- repository submission-file skeletons
- initial tests and configuration

### What I Verified Myself

- The system must reject unsafe image matches rather than always returning the nearest result.
- Vision output must be schema validated.
- The capstone requires a separate public repository.
- README, capstone.yaml, EVIDENCE.md, BUILDLOG.md, and .env.example are required submission files.
- Secrets must remain outside the repository.

### Corrections / Decisions

No model-generated implementation was treated as complete until it was run and verified locally.


## Phase 2 — Vision Processing

### AI Assistance

AI helped draft:

- Gemini vision integration
- structured image metadata extraction
- retry logic
- confidence-based review flags
- AI cost and usage tracking
- batch image-processing workflow

### What I Verified Myself

I tested the vision endpoint with multiple real images, including:

- red fox
- cattle
- lion
- dog
- wolf

The API returned structured metadata containing:

- subject
- category
- attributes
- caption
- confidence

### Corrections / Decisions

The originally configured Gemini model was no longer available to new users.

The API returned a 404 indicating that the model needed to be updated. The configuration was changed to the currently available Gemini model and the vision workflow was retested successfully.

Token usage tracking was also added after the initial implementation so vision calls record input and output units.

Low-confidence behavior was separated into deterministic logic so it could be tested without relying on an AI model returning an uncertain result.


## Phase 3 — Semantic Matching and Persistence

### AI Assistance

AI helped draft:

- embedding generation
- cosine-similarity ranking
- PostgreSQL models
- Alembic migrations
- post-image matching
- mismatch guard logic
- human-readable rejection reasons

### What I Verified Myself

PostgreSQL persistence was configured using Neon.

Alembic migrations successfully created the required database structures.

A red-fox post was tested against multiple stored images.

The selected result was:

- subject: red fox
- similarity score: 0.8558015704951459
- guard accepted: true

A wolf candidate received:

- similarity score: 0.7684449545382578
- guard accepted: false
- reason: Subject mismatch: expected red fox, detected wolf.

Other incorrect candidates including cattle, Golden Retriever, and lion were also rejected.

### Corrections / Decisions

Testing showed that unrelated animal images could still receive moderately high semantic similarity scores.

For example, cattle and lion images could have similarity scores above 0.75 for a red-fox article.

Because of this, similarity was not treated as sufficient evidence for acceptance.

A separate deterministic mismatch guard checks subject, category, confidence, and similarity before a candidate can be accepted.

The system also returns an explicit `no_confident_match` result when every available candidate fails the guard.


## Phase 4 — Review, Background Processing and Evaluation

### AI Assistance

AI helped draft:

- review persistence and API endpoints
- asynchronous background batch workflow
- job status tracking
- labeled evaluation runner
- subject alias handling
- final evidence and documentation structure

### What I Verified Myself

Automated tests reached:

15 passed

The evaluation was run against a labeled 10-case dataset.

Measured result:

- total cases: 10
- correct top-1 results: 10
- top-1 precision: 1.0 (100%)

The evaluation included:

- red fox
- wolf
- dog / Golden Retriever
- cattle
- lion

### Corrections / Decisions

The first evaluation contained five cases and achieved 80% top-1 precision.

The failed case expected `dog`, while the vision system had correctly classified the image more specifically as `Golden Retriever`.

Subject aliases were therefore added so valid subtype relationships can be recognized without weakening the mismatch guard.

The evaluation set was expanded to 10 labeled examples and rerun.

Final measured top-1 precision was 100% (10/10).

This result is reported specifically for the current small labeled evaluation set and is not presented as evidence of 100% accuracy on unseen images or categories.


## Final Engineering Decisions

The final implementation follows these principles:

1. Vision output is schema validated before use.
2. Image metadata and embeddings are persisted.
3. Semantic similarity is used for ranking, not as the only acceptance criterion.
4. Deterministic mismatch checks can override semantic similarity.
5. Unsafe or unsuitable candidates are rejected with human-readable explanations.
6. The system can explicitly return no confident match.
7. AI usage is logged for cost and usage visibility.
8. Batch image processing uses retries and background execution.
9. Human review decisions are persisted.
10. Retrieval quality is measured using a labeled evaluation set.
11. Database changes are managed through Alembic migrations.
12. Secrets are kept outside version control.


## Current Limitations

- The labeled evaluation set is small and focuses on the seeded image categories.
- The measured 100% precision should not be generalized to unseen domains.
- The in-process background-job implementation is appropriate for this capstone scale but a production deployment could use a durable queue such as Celery, RQ, or another worker system.
- Larger image collections would benefit from a dedicated vector index such as pgvector.


## Final Status

Core capstone pipeline implemented and locally verified:

Image
→ Vision metadata
→ Schema validation
→ Embedding
→ PostgreSQL persistence
→ Semantic ranking
→ Mismatch guard
→ Safe recommendation or rejection
→ Human review
→ Evaluation
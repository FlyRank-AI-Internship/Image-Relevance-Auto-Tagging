# EVIDENCE

This document records evidence for the major Definition-of-Done requirements of the FlyRank AI Image Relevance capstone.

## AI Processing

### Structured vision output validated against schema

Status: Complete.

Proof:

```text
POST /images/analyze

Example result:

subject: red fox
category: animal
confidence: 0.98
```

Vision responses are returned as structured JSON and validated through the `ImageMetadata` Pydantic schema before being accepted by the application.

Additional real-image tests successfully identified subjects including cattle, lion, Golden Retriever, wolf, and red fox.


### Low-confidence classifications are flagged

Status: Complete through deterministic test.

Proof:

```text
test_low_confidence_image_is_flagged

confidence: 0.42
threshold: 0.70

needs_review: true

review_reason:
Vision confidence below threshold: 0.42 < 0.70
```

The confidence decision is implemented deterministically so the safety behavior can be tested without depending on a vision model to intentionally produce a low-confidence response.


### Images processed through a background batch job with retries

Status: Implemented.

Proof from batch processing:

```text
POST /images/process-batch

total: 7
succeeded: 7
failed: 0
```

Retry behavior is implemented through:

```text
process_image_with_retry
```

The application also exposes:

```text
GET /jobs/{job_id}
```

for background job status tracking.

Final asynchronous execution evidence should be captured from a `202 Accepted` batch request and subsequent completed job-status response if required by the evaluator.


### Vision and embedding costs tracked per call

Status: Complete.

Proof:

```text
GET /ai-costs

provider: gemini
model: gemini-3.6-flash
call_type: vision

input_units: 1163
output_units: 70
estimated_cost: 0
```

Vision and embedding operations are logged through the AI cost tracker.

Recorded fields include:

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

The zero estimated cost reflects the current cost-estimation configuration rather than an assumption that provider usage is universally free.


## Matching System

### Image and post embeddings stored; ranked suggestions returned

Status: Complete.

Proof:

```text
GET /posts/1/images

status: matched

selected image_id: 5
selected subject: red fox
similarity_score: 0.8558015704951459

guard accepted: true
```

The relevant red-fox image ranked above the other stored candidates.


### Semantic matching works

Status: Complete.

Proof:

```text
"red fox" vs "Vulpes vulpes"

similarity:
0.9139339832713821
```

Compared with:

```text
"red fox" vs unrelated database text

similarity:
0.7075255408116042
```

The semantically related fox concepts received the stronger embedding similarity.


### Wolf-on-fox mismatch rejected

Status: Complete.

Proof from forced candidate evaluation:

```text
POST /posts/1/images/7/check

suggestion_id: 1

Candidate:
image_id: 7
subject: wolf
category: animal
confidence: 0.95
similarity_score: 0.7684449545382578

Guard:
accepted: false

reason:
Subject mismatch: expected red fox, detected wolf.
```

This demonstrates that semantic similarity alone cannot force an unsafe recommendation.


## Safety Layer

### Deterministic mismatch guard

Status: Complete.

The matching pipeline separates semantic retrieval from deterministic acceptance.

Candidate checks include:

```text
similarity
vision confidence
category compatibility
subject compatibility
```

A candidate can therefore rank semantically close to the article while still being rejected.


### Human-readable rejection explanations

Status: Complete.

Observed examples include:

```text
Subject mismatch: expected red fox, detected wolf.

Subject mismatch: expected red fox, detected Golden Retriever.

Subject mismatch: expected red fox, detected Male lion.

Subject mismatch: expected red fox, detected Cattle on a grassy hillside.
```

The API therefore explains why a candidate was rejected rather than returning only a boolean result.


### No confident match behavior

Status: Complete.

Proof:

```text
GET /posts/1/images

status: no_confident_match
selected: null

message:
No confident match found. Candidates failed similarity,
confidence, category, or subject checks.
```

This behavior was observed before a suitable red-fox image was added to the database.

The system therefore prefers explicit rejection over returning an unsuitable image.


## Backend

### PostgreSQL persistence and migrations

Status: Complete.

PostgreSQL persistence is hosted using Neon.

Initial migration proof:

```text
alembic upgrade head

Context impl PostgresqlImpl.
Will assume transactional DDL.

Running upgrade -> 5d3ff392f87a,
Create images and posts tables
```

Additional migrations were created as the review and suggestion workflows were introduced.

Alembic is used to manage schema evolution instead of relying on manual database creation.


### Image persistence

Status: Complete.

Proof:

```text
POST /images/analyze

image_id: 1

subject: Male lion
category: animal
confidence: 0.98
```

The generated `image_id` demonstrates that analyzed metadata was persisted rather than existing only in the API response.


### Post persistence

Status: Complete.

Proof:

```text
POST /posts

id: 1
title: The behavior of red foxes
expected_subject: red fox
expected_category: animal
```

The persisted post was subsequently used by the matching endpoints.


### Forced candidate check API

Status: Complete.

Proof:

```text
POST /posts/1/images/7/check

HTTP 200

suggestion_id: 1
subject: wolf
similarity_score: 0.7684449545382578

accepted: false

reason:
Subject mismatch: expected red fox, detected wolf.
```

This endpoint allows the evaluator to deliberately force an incorrect candidate through the guard.


### Review / suggestion workflow

Status: Complete.

Proof:

```text
POST /suggestions/1/reject

HTTP 200
```

Response:

```text
suggestion_id: 1
review_status: rejected
message: Suggestion rejected.
```

This verifies that a generated suggestion can be reviewed and its rejection persisted.

The application also exposes:

```text
POST /suggestions/{suggestion_id}/approve
POST /suggestions/{suggestion_id}/reject
GET  /suggestions/{suggestion_id}
```

An earlier `approve` request returned `Suggestion not found` because it was executed before suggestion ID 1 had been created. After the forced candidate check created suggestion ID 1, the reject operation succeeded.


## Quality & Documentation

### Automated tests

Status: Complete for current test suite.

Proof:

```text
pytest

15 passed, 2 warnings
```

The warnings observed were dependency deprecation warnings and did not cause test failures.

The test suite covers core behavior including:

- health endpoint
- image metadata schema validation
- confidence flagging
- AI cost-log isolation
- cosine similarity
- mismatch guard acceptance/rejection
- wolf-on-fox rejection
- review-related validation


### Labeled evaluation set and Top-1 precision

Status: Complete.

The evaluation set contains 10 labeled article-image cases.

Proof:

```text
POST /eval/run

total: 10
correct: 10
top_1_precision: 1.0
```

Measured result:

```text
Top-1 precision: 100% (10/10)
```

Evaluation categories included:

```text
red fox
wolf
dog / Golden Retriever
cattle
lion
```

Example results:

```text
Red fox:
expected: red fox
top result: red fox
score: 0.8336026356847022
correct: true

Wolf:
expected: wolf
top result: wolf
score: 0.8006668828277659
correct: true

Dog:
expected: dog
top result: Golden Retriever
score: 0.7753339573857561
correct: true

Cattle:
expected: cattle
top result: Cattle on a grassy hillside
score: 0.8893401976333406
correct: true

Lion:
expected: lion
top result: Male lion
score: 0.8435586816814337
correct: true
```

The first five-case evaluation achieved:

```text
4/5 correct
Top-1 precision: 0.8
```

The failed case expected `dog`, while the vision model identified the image more specifically as `Golden Retriever`.

Explicit subject aliases were added to recognize valid subtype relationships. The evaluation set was then expanded to 10 cases and rerun.

Final result:

```text
10/10 correct
Top-1 precision: 1.0
```

The 100% result applies only to the current small labeled evaluation set and should not be interpreted as 100% accuracy on unseen categories.


### README and architecture

Status: Complete.

README documents:

- project purpose
- implemented technology stack
- system architecture
- safety/mismatch design
- PostgreSQL setup
- API endpoints
- local installation
- migration command
- run command
- test command
- AI usage tracking
- human review workflow
- evaluation methodology
- measured Top-1 precision
- known limitations

The documented pipeline is:

```text
Image ingestion
      |
      v
Vision metadata extraction
      |
      v
Schema validation
      |
      v
Embedding generation
      |
      v
PostgreSQL persistence
      |
      v
Semantic ranking
      |
      v
Mismatch guard
     / \
    v   v
Match  No confident match
    |
    v
Human review
    |
    v
Evaluation
```


## Definition-of-Done Summary

| Requirement | Status |
|---|---|
| Structured vision metadata | Complete |
| Schema validation | Complete |
| Low-confidence flagging | Complete |
| Retry logic | Complete |
| AI usage/cost tracking | Complete |
| Image embeddings | Complete |
| Post embeddings | Complete |
| PostgreSQL persistence | Complete |
| Semantic ranking | Complete |
| Deterministic mismatch guard | Complete |
| Wolf-on-fox rejection | Complete |
| Human-readable explanations | Complete |
| No-confident-match behavior | Complete |
| Forced candidate check | Complete |
| Review / suggestion persistence | Complete |
| Alembic migrations | Complete |
| Automated tests | Complete |
| Labeled evaluation | Complete |
| Measured Top-1 precision | 100% (10/10) |
| README / architecture | Complete |

## Final Verified Results

```text
Automated tests:
15 passed

Evaluation:
10 / 10 correct
Top-1 precision: 100%

Forced mismatch:
red-fox post + wolf image
-> rejected

Reason:
Subject mismatch: expected red fox, detected wolf.

Human review:
suggestion_id 1
-> rejected successfully
```
# Phase 1 Design — AI Image Understanding & Content Matching Engine

## 1. Problem

Blog systems often select images using filenames, keywords, or weak semantic signals. This can produce visually plausible but incorrect matches, such as recommending a wolf image for an article about red foxes.

This project will build a backend service that understands what is actually present in each image, represents both images and posts semantically, ranks candidates, and refuses unsafe matches when confidence is too low.

The product goal is:

> Good suggestions when confident, safe rejection when uncertain.

## 2. Image metadata schema

Every image processed by the vision model must produce structured data in this shape:

```json
{
  "subject": "red fox",
  "category": "animal",
  "attributes": ["orange fur", "wild", "forest"],
  "caption": "A red fox standing in a forest",
  "confidence": 0.94
}
```

Rules:

- `subject`: required non-empty string
- `category`: required non-empty string
- `attributes`: list of strings
- `caption`: required non-empty string
- `confidence`: float from 0.0 to 1.0
- invalid model output is rejected
- low-confidence output is flagged for review

## 3. Data model

### Image
- id
- file_path
- source_url
- status
- created_at

### ImageMetadata
- id
- image_id
- subject
- category
- attributes
- caption
- confidence
- needs_review
- raw_model_response
- created_at

### ImageEmbedding
- id
- image_id
- vector
- model
- created_at

### Post
- id
- title
- body
- created_at

### PostEmbedding
- id
- post_id
- vector
- model
- created_at

### Suggestion
- id
- post_id
- image_id
- similarity_score
- guard_status
- guard_reason
- created_at

### Review
- id
- suggestion_id
- decision
- notes
- reviewed_at

### AICallLog
- id
- call_type
- provider
- model
- input_units
- output_units
- estimated_cost
- entity_type
- entity_id
- created_at

## 4. API surface

### Health
- `GET /health`

### Images
- `POST /images`
- `GET /images`
- `GET /images/{image_id}`
- `POST /images/process-batch`

### Posts
- `POST /posts`
- `GET /posts/{post_id}`

### Matching
- `GET /posts/{post_id}/images`
- `POST /posts/{post_id}/images/{image_id}/check`

### Review
- `POST /suggestions/{suggestion_id}/approve`
- `POST /suggestions/{suggestion_id}/reject`
- `GET /suggestions/{suggestion_id}`

### Evaluation
- `POST /eval/run`

## 5. Layer sketch

```text
HTTP/API layer
    |
    v
Application/services
    |
    +--> Vision service
    +--> Embedding service
    +--> Matching service
    +--> Mismatch guard
    +--> Review service
    |
    v
Repositories / persistence
    |
    v
PostgreSQL
```

Slow image classification and embedding work will run outside the request path as background/batch jobs.

## 6. Matching strategy

1. Process each image with a vision model.
2. Validate structured metadata.
3. Embed the image caption/metadata.
4. Embed article title + body.
5. Compute cosine similarity.
6. Rank candidates by semantic similarity.
7. Run each high-ranked candidate through the mismatch guard.
8. Return the first candidate that clears the guard.
9. If none clears the guard, return `no confident match` with reasons.

## 7. Initial mismatch guard rules

The exact thresholds will be tuned using the labeled evaluation set, not guessed.

Initial rule categories:

- Reject if image metadata is invalid.
- Reject or flag if vision confidence is below the configured threshold.
- Reject if candidate similarity is below the configured threshold.
- Reject when the article's expected subject conflicts with the detected image subject.
- Reject when the semantic category is incompatible.
- Return a human-readable reason for every rejection.

## 8. Dataset plan

Target corpus: approximately 50 licensed-free images across a few animal categories.

Initial categories:

- red fox
- wolf
- dog
- bear
- deer

Images will come from Unsplash or Pexels and will be committed only when file sizes are reasonable; otherwise a reproducible download/seed script will be provided.

A small labeled evaluation set will map posts to their correct image(s), including deliberate mismatch cases.

## 9. Explicit non-goal

This project will not build a full public-facing image search website or a polished frontend.

The capstone focuses on backend reliability: structured vision output, semantic matching, mismatch rejection, background processing, cost tracking, review endpoints, tests, and evaluation.

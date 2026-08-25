# BUILDLOG

## Phase 1 — Project setup

### AI assistance
AI was used to help translate the capstone requirements into:
- the initial backend folder structure
- the one-page design document
- the first Pydantic schema
- the repository submission-file skeletons

### What I verified myself
- The project must reject unsafe image matches rather than always returning the nearest result.
- Vision output must be schema validated.
- The capstone requires a separate public repository.
- README, capstone.yaml, EVIDENCE.md, BUILDLOG.md, and .env.example are required submission files.

### What still needs implementation
- database models and migrations
- real Gemini vision calls
- embeddings
- batch processing with retries
- cost tracking
- mismatch thresholds
- review workflow
- evaluation set
- acceptance tests

### Corrections / decisions
No model-generated implementation is being treated as complete until it is run and verified locally.

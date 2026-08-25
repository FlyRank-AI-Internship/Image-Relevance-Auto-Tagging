from app.services.embedding_service import EmbeddingService
from app.services.similarity import cosine_similarity


service = EmbeddingService()

fox_a = service.embed_text(
    "A red fox in a forest",
    entity_type="test",
    entity_id="fox-a",
)

fox_b = service.embed_text(
    "Vulpes vulpes living in woodland",
    entity_type="test",
    entity_id="fox-b",
)

database = service.embed_text(
    "PostgreSQL database indexing",
    entity_type="test",
    entity_id="database",
)

print(
    "Fox vs fox:",
    cosine_similarity(fox_a, fox_b),
)

print(
    "Fox vs database:",
    cosine_similarity(fox_a, database),
)
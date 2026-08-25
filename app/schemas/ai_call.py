from datetime import datetime

from pydantic import BaseModel


class AICallLogEntry(BaseModel):
    call_type: str
    provider: str
    model: str
    entity_type: str
    entity_id: str | None = None
    input_units: int | None = None
    output_units: int | None = None
    estimated_cost: float
    created_at: datetime
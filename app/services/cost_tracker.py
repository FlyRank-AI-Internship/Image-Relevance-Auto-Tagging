from datetime import datetime, timezone
from pathlib import Path
import json

from app.schemas.ai_call import AICallLogEntry


LOG_FILE = Path("data/ai_cost_log.jsonl")
LOG_FILE.parent.mkdir(parents=True, exist_ok=True)


def log_ai_call(
    *,
    call_type: str,
    provider: str,
    model: str,
    entity_type: str,
    entity_id: str | None = None,
    input_units: int | None = None,
    output_units: int | None = None,
    estimated_cost: float = 0.0,
) -> AICallLogEntry:

    entry = AICallLogEntry(
        call_type=call_type,
        provider=provider,
        model=model,
        entity_type=entity_type,
        entity_id=entity_id,
        input_units=input_units,
        output_units=output_units,
        estimated_cost=estimated_cost,
        created_at=datetime.now(timezone.utc),
    )

    with LOG_FILE.open("a", encoding="utf-8") as handle:
        handle.write(entry.model_dump_json() + "\n")

    return entry


def read_ai_cost_log() -> list[AICallLogEntry]:
    if not LOG_FILE.exists():
        return []

    entries: list[AICallLogEntry] = []

    with LOG_FILE.open("r", encoding="utf-8") as handle:
        for line in handle:
            if line.strip():
                entries.append(
                    AICallLogEntry.model_validate_json(line)
                )

    return entries
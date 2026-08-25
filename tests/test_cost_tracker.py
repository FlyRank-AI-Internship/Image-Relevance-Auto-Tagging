from pathlib import Path

import app.services.cost_tracker as cost_tracker


def test_ai_call_log_entry(tmp_path, monkeypatch):
    test_log = tmp_path / "ai_cost_log.jsonl"

    monkeypatch.setattr(
        cost_tracker,
        "LOG_FILE",
        test_log,
    )

    entry = cost_tracker.log_ai_call(
        call_type="vision",
        provider="gemini",
        model="test-model",
        entity_type="image",
        entity_id="fox.jpg",
        estimated_cost=0.0,
    )

    assert entry.call_type == "vision"
    assert entry.provider == "gemini"
    assert entry.entity_id == "fox.jpg"

    assert test_log.exists()
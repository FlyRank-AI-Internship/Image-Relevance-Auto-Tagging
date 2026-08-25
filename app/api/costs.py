from fastapi import APIRouter

from app.services.cost_tracker import read_ai_cost_log


router = APIRouter(
    prefix="/ai-costs",
    tags=["AI Costs"],
)


@router.get("")
def get_ai_costs():
    entries = read_ai_cost_log()

    total_cost = sum(
        entry.estimated_cost
        for entry in entries
    )

    return {
        "total_calls": len(entries),
        "estimated_total_cost": total_cost,
        "entries": entries,
    }
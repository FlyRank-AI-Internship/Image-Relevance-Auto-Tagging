from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.services.eval_service import run_evaluation


router = APIRouter(
    prefix="/eval",
    tags=["evaluation"],
)


@router.post("/run")
def run_eval(
    db: Session = Depends(get_db),
):
    return run_evaluation(db)
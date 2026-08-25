from threading import Lock
from uuid import uuid4


_jobs: dict[str, dict] = {}
_lock = Lock()


def create_job() -> str:
    job_id = str(uuid4())

    with _lock:
        _jobs[job_id] = {
            "job_id": job_id,
            "status": "queued",
            "result": None,
            "error": None,
        }

    return job_id


def update_job(
    job_id: str,
    **values,
) -> None:
    with _lock:
        if job_id in _jobs:
            _jobs[job_id].update(values)


def get_job(job_id: str):
    with _lock:
        job = _jobs.get(job_id)

        if job is None:
            return None

        return dict(job)
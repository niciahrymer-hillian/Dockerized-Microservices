"""A trimmed version of the Full-Stack-Job-Board API (C-1) — just the two
routes this lesson's containerization story needs. No database: an in-memory
list keeps the focus on Docker/Compose/Nginx/Celery, not re-teaching
SQLAlchemy. The full app with persistence is C-1; this is "the same app,
containerized," not a separate product.
"""
from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel

from app.tasks import send_application_notification

app = FastAPI(title="Dockerized Job Board API")

JOBS = [
    {"id": 1, "title": "Backend Engineer", "location": "Remote"},
    {"id": 2, "title": "Site Reliability Engineer", "location": "Wilmington, DE"},
]


class ApplyRequest(BaseModel):
    applicant_email: str


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.get("/jobs")
def list_jobs() -> list[dict]:
    return JOBS


@app.post("/jobs/{job_id}/apply", status_code=status.HTTP_202_ACCEPTED)
def apply_to_job(job_id: int, payload: ApplyRequest) -> dict:
    if not any(j["id"] == job_id for j in JOBS):
        raise HTTPException(status.HTTP_404_NOT_FOUND, "No such job")
    # Enqueue and return immediately — the 2-second "email" happens on the
    # worker, off this request's critical path.
    task = send_application_notification.delay(job_id, payload.applicant_email)
    return {"job_id": job_id, "task_id": task.id, "status": "queued"}

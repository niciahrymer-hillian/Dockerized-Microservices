"""Background jobs — work that must happen, but must not block the request
that triggered it. `apply_to_job` below is what `POST /jobs/{id}/apply`
enqueues instead of doing this work inline.
"""
import logging
import time

from app.celery_app import celery_app

logger = logging.getLogger("worker")
logging.basicConfig(level=logging.INFO)


@celery_app.task(name="app.tasks.send_application_notification")
def send_application_notification(job_id: int, applicant_email: str) -> dict:
    """Simulate emailing the employer that a new application arrived.

    A real version would call an email provider's API. The 2-second sleep
    stands in for that network round trip — long enough that doing it
    inline on the request thread would be a visibly slow POST /apply.
    """
    logger.info("Notifying employer: job=%s applicant=%s — sending...", job_id, applicant_email)
    time.sleep(2)
    logger.info("Notification sent for job=%s applicant=%s", job_id, applicant_email)
    return {"job_id": job_id, "applicant_email": applicant_email, "status": "sent"}

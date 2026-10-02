"""The Celery app instance — shared by the API (to enqueue tasks) and the
worker (to consume them). Same image, same code, two different `command:`
entries in docker-compose.yml.
"""
import os

from celery import Celery

REDIS_URL = os.environ.get("REDIS_URL", "redis://redis:6379/0")

celery_app = Celery(
    "job_board",
    broker=REDIS_URL,
    backend=REDIS_URL,
    # The worker process starts from THIS module (`-A app.celery_app`) and
    # never imports app.main — without `include`, @celery_app.task in
    # app/tasks.py never runs on the worker, so the task is never
    # registered and silently sits in the queue forever.
    include=["app.tasks"],
)

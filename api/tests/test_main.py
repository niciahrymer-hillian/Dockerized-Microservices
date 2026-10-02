from unittest.mock import patch

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health():
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}


def test_list_jobs():
    resp = client.get("/jobs")
    assert resp.status_code == 200
    jobs = resp.json()
    assert len(jobs) == 2
    assert jobs[0]["title"] == "Backend Engineer"


def test_apply_to_unknown_job_404():
    resp = client.post("/jobs/999/apply", json={"applicant_email": "a@example.com"})
    assert resp.status_code == 404


def test_apply_enqueues_task_without_blocking():
    # Patch .delay so the test doesn't need a real Redis broker running —
    # it asserts the route enqueues the task, not that Celery/Redis works.
    with patch("app.main.send_application_notification.delay") as mock_delay:
        mock_delay.return_value.id = "fake-task-id"
        resp = client.post("/jobs/1/apply", json={"applicant_email": "a@example.com"})
    assert resp.status_code == 202
    body = resp.json()
    assert body["status"] == "queued"
    assert body["task_id"] == "fake-task-id"
    mock_delay.assert_called_once_with(1, "a@example.com")

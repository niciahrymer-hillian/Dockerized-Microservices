# 🐳 Dockerized-Microservices
### Containerize the job board — Docker Compose, Nginx, Celery, GHCR.

![Chain C](https://img.shields.io/badge/Chain%20C-Project%202-378ADD?style=for-the-badge) [![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue?style=for-the-badge)](LICENSE-GPL) [![License: AGPL v3](https://img.shields.io/badge/License-AGPLv3-blue?style=for-the-badge)](LICENSE-AGPL)

[📖 Lesson Plan](docs/LESSON_PLAN.md) · [🚀 Live Demo](#)

<!-- SCREENSHOT PLACEHOLDER: docs/screenshots/overview.png -->

> **Why this matters:** Docker Compose + a reverse proxy + a background-job
> queue is the default local-dev and small-production shape for any API that
> can't do everything inline — hired for as *Backend/Platform Engineer* and
> *DevOps/SRE*. It's the exact pattern C-4 later deploys to Kubernetes.

## Why This Was Built

The job board works on my machine, which is exactly the problem. Containerising it forces every implicit
dependency into the open — the Python version, the Redis it assumes, the environment variables it silently
reads — and turns "works here" into something reproducible anywhere.

I want to do it properly rather than wrapping everything in one fat image: separate services, a reverse
proxy in front, a worker for background jobs, and images small enough that a rebuild isn't a coffee break.

## Tech Stack

| Technology | Version | Purpose |
|-----------|---------|---------|
| Docker | — | Package each service with its dependencies into a reproducible image |
| Docker Compose | — | Orchestrate API, worker, database, and proxy together locally |
| Nginx | — | Reverse proxy and static file serving in front of the app |
| Celery | — | Run background jobs off the request path |
| Redis | — | Broker for Celery and cache for the API |
| GHCR | — | Host the built images for deployment |

## Project Structure

```
Dockerized-Microservices/
├── api/                    # FastAPI app — same image used by the api AND worker services
│   ├── app/
│   │   ├── main.py         # GET /jobs, POST /jobs/{id}/apply (enqueues, returns 202)
│   │   ├── celery_app.py   # Celery() instance, broker=redis
│   │   └── tasks.py        # send_application_notification — runs on the worker
│   ├── tests/test_main.py
│   ├── requirements.txt
│   └── Dockerfile          # multi-stage: build deps, then slim runtime
├── frontend/index.html     # static SPA stand-in, served by nginx
├── nginx/nginx.conf        # reverse proxy: /api/ -> api:8000, / -> static files
├── docker-compose.yml      # redis, api, worker, nginx — healthcheck-gated depends_on
├── .github/workflows/ci.yml
├── .env.example
├── docs/{LESSON_PLAN.md, interactive/index.html, screenshots/}
├── LICENSE-GPL
└── LICENSE-AGPL
```

## Getting Started

```bash
git clone https://github.com/niciahrymer-hillian/Dockerized-Microservices.git
cd Dockerized-Microservices
# Build and start the whole stack
docker compose up --build

# The API is proxied through Nginx
open http://localhost:8080

# Watch the worker pick up a background job
docker compose logs -f worker
```

## Chain Navigation

Part of **Chain C — Full-Stack + Infrastructure** in the [Post-Bootcamp-Challenge](https://github.com/niciahrymer-hillian/Post-Bootcamp-Challenge) portfolio.

---

Dual licensed — [GPL v3](LICENSE-GPL) and [AGPL v3](LICENSE-AGPL).

# 📖 Lesson Plan — Dockerized-Microservices

| Field | Value |
|-------|-------|
| Chain | Chain C — Full-Stack + Infrastructure (project C-2 of 4) |
| Difficulty | Intermediate |
| Estimated time | ~2.5 weeks |
| Prerequisite | [Full-Stack-Job-Board](../../Full-Stack-Job-Board) (C-1) |
| Next project | [Ops-Management-Dashboard](../../Ops-Management-Dashboard) (C-3) |
| Primary license | GPL v3 (local infra/orchestration), AGPL v3 for the deployed services |
| From scratch | No — skeleton scaffold (working bones + TODOs) |

## What This Project Is

C-1 built a job board that "works on my machine." This project containerizes
it: every implicit dependency (Python version, the Redis it assumes, env vars
it silently reads) becomes an explicit, reproducible image. Four services —
`api`, `worker`, `redis`, `nginx` — run together under one
`docker compose up`, with Nginx as the single public door in front of two
upstreams that are otherwise invisible from outside the Docker network.

The app itself is deliberately trimmed from C-1 (no database — an in-memory
job list) so the lesson stays focused on **orchestration**, not re-teaching
SQLAlchemy. The new piece is `POST /jobs/{id}/apply` enqueuing a Celery task
instead of doing the (simulated) 2-second "send an email" work inline — the
same request/background-job split C-1's own LESSON_PLAN assumed existed by
C-4's time but this project is where it's actually built.

## Learning Objectives

- Explain why `COPY requirements.txt` + `pip install` has to come *before*
  `COPY app/` in a Dockerfile, and what breaks (rebuild speed, not
  correctness) if you get the order backwards.
- Write a Docker Compose file where a dependent service genuinely waits for
  its dependency to be *ready*, not just *started* (`condition: service_healthy`).
- Explain Docker's embedded DNS: why `nginx.conf` can say `proxy_pass http://api:8000/`
  with no IP address anywhere.
- Configure Nginx as a reverse proxy splitting traffic between an API path
  and a static-file fallback, and explain what `try_files $uri /index.html`
  is for.
- Run the same application image as two different processes (a web server
  and a Celery worker) via two different `command:` overrides on one `build:`.
- Explain the two-job CI/CD shape: a `test` job that gates a `build-and-push`
  job via `needs:`, so a failing test can never reach the registry.

## Software You Will Use

| Tool | What it is | Why it matters here | Install | Docs |
|------|-----------|----------------------|---------|------|
| Docker | Container runtime | Packages each service with its own dependencies | [docs.docker.com/get-started](https://docs.docker.com/get-started/) | [Docker — Multi-Stage Builds](https://docs.docker.com/build/building/multi-stage/) |
| Docker Compose | Multi-container orchestration | One command (`docker compose up`) runs all 4 services wired together | bundled with Docker Desktop | [Compose — Control Startup Order](https://docs.docker.com/compose/how-tos/startup-order/) |
| Nginx | Reverse proxy / web server | Single public port fronting the api and the static frontend | `nginx:1.27-alpine` (no local install needed) | [Nginx — Reverse Proxy](https://docs.nginx.com/nginx/admin-guide/web-server/reverse-proxy/) |
| Celery | Distributed task queue | Runs `send_application_notification` off the request path | `pip install "celery[redis]"` | [Celery — First Steps](https://docs.celeryq.dev/en/stable/getting-started/first-steps-with-celery.html) |
| Redis | In-memory data store | Celery's broker (task queue) and result backend | `redis:7-alpine` (no local install needed) | [Redis docs](https://redis.io/docs/latest/) |
| GitHub Container Registry | Docker/OCI image registry | Where CI pushes the built, SHA-tagged image | — | [GHCR — Working with the Container Registry](https://docs.github.com/en/packages/working-with-a-github-packages-registry/working-with-the-container-registry) |

## The Service Topology

```
                    ┌────────────────────────────┐
  host:8080 ───────▶│  nginx  (public, port 80)  │
                    └───────────┬────────────────┘
                   /api/ ──────┤└────── / (static)
                    ▼                        ▼
          ┌──────────────────┐      frontend/index.html
          │   api  (8000)    │
          └─────────┬────────┘
                     │ .delay()
                     ▼
          ┌──────────────────┐      ┌──────────────────┐
          │   redis (broker) │◀────▶│  worker (same     │
          └──────────────────┘      │  image as api)    │
                                     └──────────────────┘
```

`api` and `worker` are **the same built image** — `docker-compose.yml` gives
them different `command:` entries, not different `build:` contexts.

## Build Order

- **Week 1 — Containerize the API alone.** Write `api/Dockerfile` (multi-stage),
  `api/app/main.py` with the trimmed `/jobs` + `/jobs/{id}/apply` routes.
  *Verify: `docker build -t jb-api ./api && docker run -p 8000:8000 jb-api`,
  then `curl localhost:8000/health`.*
- **Week 1.5 — Add Celery + Redis.** `celery_app.py`, `tasks.py`, wire
  `REDIS_URL` through `.env.example`. Add `redis` and `worker` to
  `docker-compose.yml` with a healthcheck on `redis` and
  `depends_on: {redis: {condition: service_healthy}}` on both `api` and `worker`.
  *Verify: `docker compose up`, then `docker compose logs -f worker` while
  you `curl -X POST localhost:8000/jobs/1/apply` from another terminal — the
  worker log should show the task running, 2 seconds later, "sent."*
- **Week 2 — Nginx in front.** Write `nginx/nginx.conf` with the `/api/` and
  `/` location blocks, add `nginx` to compose mapping host `8080` to
  container `80`. *Verify: the SAME curl commands above now go through
  `localhost:8080/api/...` instead of talking to `api` directly — devtools'
  Network tab should show only port 8080.*
- **Week 2.5 — CI/CD.** `.github/workflows/ci.yml`: a `test` job
  (`pytest api/tests/`), then a `build-and-push` job with `needs: test` that
  logs into GHCR and pushes `ghcr.io/<repo>:<git-sha>`.
  *Verify: push a branch, watch both jobs go green in the Actions tab; push
  a commit that fails a test and confirm `build-and-push` never runs.*

## Common Mistakes to Avoid

- **Reversing the Dockerfile's `COPY` order.** `COPY app/ app/` before
  `COPY requirements.txt .` + `pip install` means every single code change
  invalidates the pip-install layer, turning a one-line fix into a full
  dependency reinstall on every rebuild.
- **`depends_on` without a healthcheck condition.** Plain `depends_on: [redis]`
  only waits for the container to *start*, not for Redis to actually be
  accepting connections yet — a worker can crash-loop for the first second
  of its life purely from a race, not a real bug.
- **Forgetting `include=[...]` on the Celery app.** The worker process starts
  from `app.celery_app`, not `app.main` — if `app.tasks` is never imported
  anywhere the worker's import path touches, `@celery_app.task` never runs,
  the task is never registered, and enqueued work sits in the queue forever
  with no error anywhere. (This is a real bug this project's own first build
  hit — see the LESSON_PLAN's lesson 3 for the fix.)
- **A CI pipeline with one job that both tests and pushes.** If "run tests"
  and "build + push" are the same job, a flaky or slow push step can block
  the thing that actually signals correctness. Two jobs with `needs:` keeps
  "tests passed" as a real, independent gate.

## Why This Matters (Industry Application)

**What this skill is used for in the real world**
Almost no production service runs as "one process on one machine" anymore.
Multi-container orchestration (Compose locally, Kubernetes in production),
a reverse proxy in front, and a background-job queue for anything slower
than a request should block on, are the default shape of backend
infrastructure at nearly every company past the single-founder stage.

**Roles that hire for it**
- Backend Engineer · Platform Engineer · DevOps/SRE
- Any Full-Stack role at a company that self-hosts rather than using a PaaS

**Why it strengthens *my* portfolio**
This is the exact deployment shape Centric/Entrada and Keyholders already
need in production — a stateless API, a background-job worker for emails
and notifications, and a reverse proxy in front. Building it here first,
on a small trimmed app, means the pattern is already proven before it's
applied to the real product.

**How it connects to the rest of the portfolio**
- Builds on: [C-1 — Full-Stack-Job-Board](../../Full-Stack-Job-Board)
- Feeds into: [C-3 — Ops-Management-Dashboard](../../Ops-Management-Dashboard), [C-4 — Kubernetes-IaC-Deployment](../../Kubernetes-IaC-Deployment)

## Reflection Questions

1. Why does `COPY requirements.txt` + `pip install` need to happen before `COPY app/`, and what specifically does getting this backwards cost you?
2. What's the practical difference between `depends_on: [redis]` and `depends_on: {redis: {condition: service_healthy}}` — what race does the second one close?
3. `api` and `worker` share one `build:` context. Why not just change the Dockerfile's `CMD` instead of overriding `command:` per service?
4. Why does `nginx.conf` reference the API as `http://api:8000` with no IP address, and what would break if you tried to hardcode an IP instead?
5. If the `build-and-push` job didn't have `needs: test`, what's the worst realistic outcome?
6. The worker silently did nothing the first time this project ran it end-to-end. What was the actual root cause, and why did it fail silently instead of raising an error?

## Topics to Research

- [Docker — Multi-Stage Builds](https://docs.docker.com/build/building/multi-stage/)
- [Docker Compose — Control Startup and Shutdown Order](https://docs.docker.com/compose/how-tos/startup-order/)
- [Nginx — Reverse Proxy (Admin Guide)](https://docs.nginx.com/nginx/admin-guide/web-server/reverse-proxy/)
- [Celery — First Steps with Celery](https://docs.celeryq.dev/en/stable/getting-started/first-steps-with-celery.html)
- [GitHub — Working with the Container Registry](https://docs.github.com/en/packages/working-with-a-github-packages-registry/working-with-the-container-registry)
- [GitHub Actions — Using Jobs in a Workflow (`needs`)](https://docs.github.com/en/actions/using-jobs/using-jobs-in-a-workflow)

## How This Connects Forward

**C-3** adds a WebSocket-driven real-time layer to a sibling ops app — the
same container-per-service thinking applies, plus a stateful connection the
load balancer has to be aware of. **C-4** takes this exact multi-container
shape and moves it from Compose (one host) to Kubernetes (many hosts) —
`nginx`'s reverse-proxy role becomes an Ingress, `depends_on` becomes a
readiness probe, and the Celery worker becomes its own Deployment that can
scale independently of the API.

## Git Commit Checklist

- [ ] Conventional commits, one feature each (`feat:`, `fix:`, `chore:`).
- [ ] Never commit `.env` — only `.env.example`.
- [ ] Verify `docker compose up --build` from a clean checkout before committing.

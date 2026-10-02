# Multi-stage build: the `builder` stage has gcc/build tools to compile any
# C-extension wheels; the final stage only copies the installed packages
# across, so the shipped image never carries a compiler it doesn't need at
# runtime. requirements.txt is copied and installed BEFORE the app code —
# that layer only invalidates when dependencies change, not on every code
# edit, so `docker compose build` reuses the pip-install layer from cache.
FROM python:3.12-slim AS builder
WORKDIR /build
COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

FROM python:3.12-slim
WORKDIR /app
COPY --from=builder /install /usr/local
COPY app/ app/

# api service overrides CMD with uvicorn; worker service overrides it with
# `celery -A app.celery_app worker` — see docker-compose.yml. This default
# is just a safe fallback if the image is run with no command at all.
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

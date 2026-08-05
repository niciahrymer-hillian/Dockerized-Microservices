# 📖 Lesson Plan — Dockerized-Microservices

> **Chain C — Full-Stack + Infrastructure** | Containerize the job board — Docker Compose, Nginx, Celery, GHCR.

## What This Project Is

Containerise a multi-service application properly: small images, Compose orchestration, health checks, and environment-driven configuration.

## Learning Objectives

By the end I can:

1. Write Dockerfiles that build small, cached images.
2. Use multi-stage builds to keep runtime images minimal.
3. Orchestrate services locally with Docker Compose.
4. Add health checks and correct startup ordering.
5. Configure via environment variables, never baked-in secrets.
6. Persist data with volumes and understand their lifecycle.

## Software You Will Use

- Docker and Docker Compose.
- A multi-service app (API, database, cache).

## Build Order

1. Containerise one service naively; note the image size.
2. Optimise with multi-stage builds and layer ordering.
3. Add a database and cache via Compose.
4. Add health checks and dependency ordering.
5. Move all configuration to environment variables.
6. Add volumes and verify data survives a restart.

## Common Mistakes to Avoid

- Baking secrets into images.
- Running as root inside the container.
- Copying the whole context and busting the layer cache every build.
- No health checks, so a service is 'up' before it is ready.
- Storing state in the container filesystem.

## Check Your Understanding

The quiz covers multi-stage builds, layer caching, health checks, and configuration handling.

## Why This Matters (Industry Application)

Containers are the default deployment unit, and Docker fluency is assumed for backend, DevOps, and data engineering roles. Image size, layer caching, and health checks are the practical details that separate a container that works locally from one that runs reliably in production.

## Reflection Questions

- What is in your image that does not need to be, and what does that cost?
- How would this Compose setup differ from a real production deployment?

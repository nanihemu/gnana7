# School Management System API

API-first, multi-tenant backend for a School Management System (SMS) with AI
integrations. One REST API serves the React web app, React Native mobile app,
and the AI pipeline.

## Roles

- **Super Admin** — manages schools (tenants), plans/subscriptions, platform
  analytics, and data-driven role privileges.
- **Admin** — one per school; manages students, teachers, classes, subjects,
  notifications, achievements, and school revenue.
- **Teacher** — subject-level; posts topics, assessments, marks, feedback, remarks.
- **Student** — views scores, practices topics (incl. AI-generated quizzes), self-study.
- **Parent** — sees their child's performance analytics, weak/strong areas,
  improvement suggestions, and payments.

## Stack

- **Backend:** Django 4.2 + Django REST Framework
- **Auth:** JWT (`djangorestframework-simplejwt`)
- **DB:** PostgreSQL (SQLite for zero-config local dev)
- **AI:** provider-agnostic services with graceful fallbacks (quiz generator,
  avatar-video job queue, RAG-ready)

## Quick start (local, SQLite)

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env            # defaults to SQLite
python manage.py migrate
python manage.py seed_roles     # creates 5 roles + superadmin/changeme123
python manage.py runserver
```

Test the health endpoint and login:

```bash
curl http://localhost:8000/api/v1/health/
curl -X POST http://localhost:8000/api/v1/auth/token/ \
  -H "Content-Type: application/json" \
  -d '{"username":"superadmin","password":"changeme123"}'
```

## Run with Docker (PostgreSQL + Redis)

```bash
docker compose up --build
```

Set Postgres connection via `DB_*` env vars in production (defaults in
`docker-compose.yml`). Configure the real DB in `config/settings.py` (reads env).

## Project structure

```
config/            # project settings, root URLs
core/              # User, Tenant, Role; JWT auth; tenant-isolation middleware;
                   #   tenant-scoped managers; seed_roles command
tenants/           # Super Admin: plans, subscriptions, platform stats, transactions
academics/         # classes, subjects, enrollments, teacher assignments, topics,
                   #   assessments, questions, submissions, feedback, remarks, analytics
ai/                # quiz generation, avatar-video job queue, (RAG chatbot next)
```

All routes are mounted under `/api/v1/` (see `config/urls.py`).

## Multi-tenancy

Every school-scoped model inherits `TenantModel` (in `core/managers.py`), which
attaches a `tenant` FK and swaps the default manager for a tenant-scoped one.
`core/middleware.py` injects the request's tenant, so ordinary ORM queries are
automatically isolated — a school can never read another school's data.

## AI services

- **Quiz generation:** `ai/services/quiz_generator.py`. Uses an LLM when
  `OPENAI_API_KEY` is set; otherwise falls back to deterministic templates so the
  system is fully runnable/testable offline.
- **Avatar video:** `ai/services/__init__.py` records a `VideoGenerationJob`;
  the TTS + avatar render (e.g. HeyGen) hooks in as an async provider.

## Roadmap

- RAG chatbot grounded in uploaded materials (pgvector)
- Natural-language parent progress summaries
- Payment gateway integration (fees)
- Notifications / achievements
- Live chat (WebSockets)

## License

Proprietary / internal.
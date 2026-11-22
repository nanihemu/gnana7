# Gnana SMS — Multi-tenant School Management System

API-first, multi-tenant School Management System (SMS) with a React web
dashboard and AI integrations. One Django REST API serves the React web app and
the AI pipeline.

## Roles

- **Super Admin** — manages schools (tenants), plans/subscriptions, platform
  analytics, and data-driven role privileges.
- **Admin** — one per school; manages students, teachers, parents, classes,
  subjects, enrollments, notifications, achievements.
- **Teacher** — posts topics/study material, runs AI quiz generation and avatar
  videos, creates assessments and questions, grades submissions with AI-drafted
  feedback, writes remarks.
- **Student** — attempts and gets auto-graded assessments, views results and
  subject-wise performance, self-study (AI quizzes + AI tutor), notifications,
  achievements.
- **Parent** — sees their children, each child's performance analytics
  (strong/weak areas) and an AI natural-language progress summary, plus
  achievements.

## Stack

- **Backend:** Django 4.2 + Django REST Framework
- **Frontend:** Vite 5 + React 18 + TypeScript + react-router + axios
- **Auth:** JWT (`djangorestframework-simplejwt`, tenant-aware authentication)
- **DB:** PostgreSQL (SQLite for zero-config local dev)
- **AI:** provider-agnostic services with graceful fallbacks. Works with any
  OpenAI-compatible API (`OPENAI_API_KEY` / `OPENAI_BASE_URL`); chat, quiz
  generation, feedback, summaries and RAG embeddings all degrade to
  deterministic modes when no model is configured.

## AI integrations

All AI runs through `ai/services` — each feature falls back to a deterministic
implementation when no LLM is configured, so the system is fully testable
offline.

- **RAG chatbot / AI tutor** — `POST /api/v1/chat/` answers a question grounded
  in the school's posted topics. Topics are embedded (OpenAI
  `text-embedding-3-small`) and compared with pure-Python cosine similarity; a
  keyword-search fallback keeps retrieval working without a provider. Returns
  `{answer, sources, grounded}`. A floating widget in the web app exposes it to
  students, teachers and parents.
- **AI quiz generation** — `POST /api/v1/quiz/generate/<topic_id>/` asks the
  LLM for MCQs matching the topic and saves them to the question bank (5
  questions; `?n=` supported). Marks `topic.quiz_generated`.
- **AI feedback + auto-grading** — MCQs are auto-graded instantly on
  submission (`academics/services.auto_grade`). Teachers can ask the model to
  draft per-question feedback for any submission:
  `POST /api/v1/feedback/<submission_id>/`.
- **Avatar video provider** — `POST /api/v1/video/<topic_id>/` writes an
  LLM-generated lesson script into a `VideoGenerationJob`. When `HEYGEN_API_KEY`
  is set it posts the script to the HeyGen v2 API (`avatar.providers`); otherwise
  it completes with provider `"fallback"` (no fake URLs).
- **Parent progress summaries** — `GET /api/v1/performance/<student_id>/summary/`
  converts subject-wise analytics into a warm, natural-language progress note
  for parents (LLM with deterministic fallback).

## Quick start (local, SQLite)

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env            # defaults to SQLite / no AI provider

python manage.py migrate
python manage.py seed_roles     # creates 5 roles + superadmin/changeme123
python manage.py seed_demo      # demo school: users, class, topics, quiz, notifications
python manage.py runserver      # backend on :8000
```

Smoke-test the API:

```bash
curl http://localhost:8000/api/v1/health/
curl -X POST http://localhost:8000/api/v1/auth/token/ \
  -H "Content-Type: application/json" \
  -d '{"username":"superadmin","password":"changeme123"}'
```

### Seed logins (password `demo12345`)

| Role          | Username     | Password    |
| ------------- | ------------ | ----------- |
| Super Admin   | `superadmin` | `changeme123` |
| School Admin  | `admin`      | `demo12345` |
| Teacher       | `teacher`    | `demo12345` |
| Student       | `student`    | `demo12345` |
| Parent        | `parent`     | `demo12345` |

The login page of the web app has one-click demo-login buttons.

## Frontend (React web app)

A Vite + React + TypeScript SPA in `frontend/`, with role-based dashboards for
all five roles and a floating AI-tutor chat widget.

```bash
cd frontend
npm install
npm run dev        # http://localhost:5173 (proxies /api -> :8000)
npm run build      # tsc + vite production build
```

- JWT is stored in `localStorage`; the axios layer attaches it and transparently
  refreshes via `/auth/token/refresh/` (single-flight), redirecting to `/login`
  on failure.
- DRF list pagination is transparently unwrapped in the shared data hook.
- `VITE_API_ROOT` overrides the API base URL in production (default `/api/v1`).

## Run with Docker (whole app in one image)

```bash
# requires a local .env (cp .env.example .env) for OPENAI_* / HEYGEN_* keys
docker compose up --build
```

The single image (multi-stage `Dockerfile`) builds the React app and embeds it
in the Django container, so `http://localhost:8000` serves **both** the web
dashboard and the API. `migrate` + `seed_roles` + `seed_demo` run
idempotently on every boot, so demo logins are ready immediately.

- Web dashboard: `http://localhost:8000` (SPA served by Django, static under
  `/static/`)
- API/health: `http://localhost:8000/api/v1/health/`
- Postgres + Redis come up via `docker compose` (`DB_*` env vars wired in
  `docker-compose.yml`; configure the real DB in `config/settings.py`).

During frontend development (live reload) keep using the Vite dev server from
`npm run dev` in `frontend/` — the SPA fallback only kicks in when
`frontend/dist` exists.

## Project structure

```
config/            # project settings, root URLs
core/              # User, Tenant, Role; tenant-aware JWT auth; tenant-isolation
                   #   middleware (thread-local); tenant-scoped managers; seed commands
tenants/           # Super Admin: tenants, plans, subscriptions, transactions, roles
academics/         # classes, subjects, enrollments, teacher assignments, topics,
                   #   assessments, questions, submissions, feedback, remarks,
                   #   notifications, achievements, performance analytics
ai/                # RAG chatbot, quiz generation, AI feedback, progress summaries,
                   #   avatar-video provider (HeyGen), LLM/embedding client
frontend/          # React 18 + Vite + TypeScript web app (5 role dashboards)
```

All routes are mounted under `/api/v1/` (see `config/urls.py`).

## Multi-tenancy

Every school-scoped model inherits `TenantModel` (in `core/managers.py`), which
attaches a `tenant` FK and swaps the default manager for a tenant-scoped one.
A tenant-aware JWT authentication class sets the request's tenant into
thread-local context (`core/middleware.py`), so ordinary ORM queries are
automatically isolated — a school can never read another school's data.
Views use `get_queryset()` (never eager class-level querysets) so the tenant
filter is applied at request time.

## Testing

```bash
DB_ENGINE=django.db.backends.sqlite3 ./venv/bin/python manage.py test academics ai tenants core
```

32 tests cover auto-grading, teacher grading, parent dashboards (incl. child
isolation), notifications/achievements, student self-study, tenant isolation,
AI quiz/video/RAG/feedback fallbacks, and super-admin platform stats.

## Roadmap

- Payment gateway integration (fees)
- Live chat (WebSockets)
- pgvector-backed retrieval at scale (current RAG is pure-Python cosine)

## License

Proprietary / internal.

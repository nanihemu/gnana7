# ---------------------------------------------------------------------------
# Gnana SMS — single image: React frontend + Django REST API.
#
#   docker compose up --build
#
# The frontend is built in the first stage so that only the compiled assets
# (frontend/dist) ship in the final image; the API, static assets and the SPA
# fallback are all served by the Django container.
# ---------------------------------------------------------------------------

# --- Stage 1: build the React web app -------------------------------------
FROM node:18-alpine AS frontend-build
WORKDIR /app
COPY frontend/package.json frontend/package-lock.json ./
RUN npm ci
COPY frontend/ ./
# Assets are served by Django under STATIC_URL, hence the /static/ base.
RUN VITE_BASE=/static/ npm run build

# --- Stage 2: Django backend (also serves the built SPA) ------------------
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

COPY . .

# Drop the compiled React app into place (findable via STATICFILES_DIRS and
# the SPA fallback view).
COPY --from=frontend-build /app/dist ./frontend/dist

EXPOSE 8000

# migrate + seed idempotently on every boot, then serve the whole app.
CMD ["sh", "-c", "python manage.py migrate && python manage.py seed_roles && python manage.py seed_demo && python manage.py runserver 0.0.0.0:8000"]

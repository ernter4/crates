# ==========================================
# STAGE 1: Schnelle Build-Umgebung (mit uv)
FROM ghcr.io/astral-sh/uv:python3.13-alpine AS builder

ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy
ENV UV_NO_DEV=1
ENV UV_PYTHON_DOWNLOADS=0

WORKDIR /app

# Kopiere die Paketlisten klassisch rein (sehr stabiles Docker-Caching)
COPY pyproject.toml uv.lock ./

# Installiere nur die Abhängigkeiten
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-install-project

# Erst jetzt den restlichen Code kopieren und das Projekt finalisieren
COPY . /app
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen
# ==========================================
# STAGE 2: Schlankes & sicheres Runtime-Image (ohne uv)
# ==========================================
FROM python:3.13-alpine

# Verhindert unvollständige Log-Ausgaben bei Abstürzen
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Sicherheits-User anlegen (kein root)
RUN adduser -D -u 1000 appuser

# Das fertige Verzeichnis inkl. der virtuellen Umgebung (.venv) rüberschieben
COPY --from=builder --chown=appuser:appuser /app /app

# Virtuelle Umgebung in den System-PATH legen
ENV PATH="/app/.venv/bin:$PATH"

# Auf den sicheren User wechseln
USER appuser

# Befehle ausführen (Alembic Migrations + FastAPI Start)
CMD ["/bin/sh", "-c", "alembic upgrade head && fastapi run main.py"]
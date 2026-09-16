# Crates

<!-- Short 1-2 sentence description: what does the app do? (FastAPI backend for Accounting & Ordering) -->

## Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Requirements](#requirements)
- [Installation](#installation)
- [Configuration](#configuration)
- [Development](#development)
- [Database & Migrations](#database--migrations)
- [Tests](#tests)
- [Deployment](#deployment)
- [Project Structure](#project-structure)
- [Changelog](#changelog)

## Overview

This is the backend for the Crates application, wich handles the accounting and ordering of Menues in Gasthof zum goldenen Lamm in Harburg(Schwaben).
It contains the following modules:
- Accounting:
  - Export to Datev
  - Create Invoices
  - Manage Customers
- Ordering:
  -  Manage Orders
  -  Manage Crates
  -  Manage Assignment of Crates to Orders ( Web_NFC/OCR)



## Architecture

- **API**: FastAPI, mounted under `/api`
- **Modules**:
  - `app/accounting` – customers, invoices, export, SEPA
  - `app/ordering` – orders, crates, assignment (Assigner), OCR
  - `app/shared` – auth, database, shared services
- **Database**: SQLAlchemy / SQLModel, migrations via Alembic
- **Package management**: [uv](https://docs.astral.sh/uv/)

## Requirements

- Python >= 3.13
- [uv](https://docs.astral.sh/uv/)
- (optional) Docker & Docker Compose

## Installation

```bash
uv sync
```

## Configuration

Environment variables are loaded from a `.env` file (see `.env`):

| Variable | Description |
|---|---|
| `CRATES_DATABASE_URL` | Database connection string |
| `CRATES_DATABASE_FILE` | Path to the SQLite file |
| `CRATES_DISABLE_AUTH` | Disable auth for local development |
| `CRATES_CORS_ALLOWED_ORIGINS` | Allowed CORS origins (comma-separated) |

## Development

```bash
uv run python main.py
# or
uv run fastapi dev main.py
```

The API is then available at `http://localhost:8000/api`.



## Tests

```bash
uv run pytest
```

## Deployment

```bash****
docker compose up --build
```
On startup, the image automatically runs `alembic upgrade head` and then starts the app via `fastapi run`.

This System is meant to be deployed within the Serverstructure displayed in [Webserver_config](https://github.com/ernter4/webserver_config)

## Project Structure

```
app/
├── accounting/        # customers, invoices, export, SEPA
├── ordering/           # orders, crates, assignment, OCR
└── shared/             # auth, DB, shared services
migrations/             # Alembic migrations
test/                   # tests (pytest)
```

## Changelog

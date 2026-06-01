# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

翻墙数据可视化系统 — a single-page web application for visualizing VPN/proxy traffic data from a PostgreSQL database. FastAPI backend serving both API and static frontend, Vue3 + Element Plus + ECharts for the UI.

## Directory Structure

```
├── docker-compose.yml          # Docker orchestration (postgres + fastapi)
├── visualization/
│   ├── CLAUDE.md               # Detailed architecture docs (read this for API/frontend details)
│   ├── README.md               # User-facing documentation
│   ├── backend/
│   │   ├── main.py             # FastAPI app — single file, all routes
│   │   ├── config.yaml         # DB/server/API config (env vars override)
│   │   ├── requirements.txt    # Python deps
│   │   ├── create_table.sql    # PostgreSQL schema
│   │   ├── create_test_data.py # Test data generator
│   │   └── Dockerfile
│   └── frontend/
│       └── index.html          # SPA entry point (Vue3 + Element Plus + ECharts via CDN)
```

## Development Commands

```bash
# Local development (no Docker)
cd visualization/backend
pip3 install -r requirements.txt
python3 main.py                   # Starts on port 8000

# Docker (full stack: postgres + fastapi)
docker-compose up -d              # Start both services
docker-compose down               # Stop services

# API docs: http://localhost:8000/docs
# Frontend: http://localhost:8000/
```

No frontend dev server needed — FastAPI serves static files from `../frontend/` via the `/{filename:path}` route.

## Architecture Summary

- **Backend**: Single-file FastAPI (`main.py`) with PostgreSQL via psycopg2. All routes defined in one file. Config loaded from `config.yaml`, overridable via env vars (`DB_HOST`, `DB_PORT`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `SERVER_HOST`, `SERVER_PORT`, `API_BASE_URL`).
- **Frontend**: Single HTML file SPA with 3 tabs (主页统计 / 翻墙详情 / 智能查询), Vue3 global build + Element Plus + ECharts loaded from CDN.
- **Database**: PostgreSQL 15, table `nb_mass_resource_all_stream` (~3717 test records, ~100 columns).

For detailed API routes, frontend component structure, database schema, and change history, see `visualization/CLAUDE.md`.

## Docker Notes

- `docker-compose.yml` defines two services: `postgres` (port 5432) and `fastapi` (port 8000).
- **Env var mismatch**: docker-compose sets `DATABASE_HOST`, `DATABASE_PORT`, etc., but `main.py` reads `DB_HOST`, `DB_PORT`, etc. The Docker env vars are not picked up — fix one side to match.
- **Dockerfile frontend copy**: `COPY ../frontend/* /home` copies files to `/home` not `/home/frontend` where the app expects them. Also, `../frontend` may be outside the Docker build context (`./visualization/backend`). Fix by adjusting the build context to project root or using `COPY --from`.

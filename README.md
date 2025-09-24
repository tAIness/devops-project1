# Super Mario – DevOps Project

A small **Mario-themed web app** with a **Flask API** and **PostgreSQL** backend, wrapped with a full CI/CD pipeline (lint, tests, security scans, Allure reports) and **Release** automation that builds and pushes container images to **Docker Hub** and mirrors to a private **Nexus** on EC2, then deploys to EC2 with Docker Compose.

> Frontend lives in `web/` (static site with a small game) and talks to the backend API in `app/`. Scores are stored in Postgres.

---

## Architecture

<img width="1374" height="922" alt="image" src="https://github.com/user-attachments/assets/363daaf9-a7b6-4b11-8f0e-78d63acc73d4" />


- **web/** – Static site served by nginx. `game/index.html` + `game.js` posts scores to `/api/score` and fetches `/api/leaderboard`. Gallery assets under `web/assets` and `web/images`.
- **app/** – Flask app exposing:
  - `GET /health` – lightweight health probe (checks DB connectivity; returns `{"status": "ok"}` or `"degraded"`).
  - `POST /api/score` – body `{"user_name": str, "result": int}` (aliases: `{"name","ms"}`); inserts a score.
  - `GET /api/leaderboard` – returns best (lowest) result per user (top 20).
- **db** – Postgres 15 container (via `deploy/compose.yml`). App uses pooled connections (`psycopg2 SimpleConnectionPool`).
- **content/** – Optional images uploaded alongside deployment.
- **e2e/** – Playwright tests and JUnit output.
- **security/** – Snyk ignores list.
- **.github/workflows/** –
  - `ci.yml` – PR checks (lint, unit, DB, E2E, image builds, Snyk, Allure → GitHub Pages, Slack).
  - `release.yml` – tag on main, build & push images (Docker Hub), mirror to Nexus, Snyk gate, deploy to EC2, Slack.

### API snippets

```bash
# Health
curl -s http://localhost:8000/health

# Insert score
curl -s -X POST http://localhost:8000/api/score \
  -H 'Content-Type: application/json' \
  -d '{"user_name":"mario","result":1234}'

# Leaderboard
curl -s http://localhost:8000/api/leaderboard | jq
```

---

## Repo layout

```
.
├── app/                 # Flask API (Gunicorn-ready) + tests
│   ├── app.py           # routes: /health, /api/score, /api/leaderboard
│   ├── db.py            # connection pool + init_db()
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── tests/           # unit & DB tests (pytest markers)
│   └── pytest.ini
├── web/                 # Static frontend (nginx)
│   ├── Dockerfile
│   ├── static/index.html
│   ├── game/index.html, game.js
│   └── nginx.conf
├── deploy/compose.yml   # App + Web + Postgres for EC2 deployment
├── e2e/                 # Playwright specs + junit.xml
├── security/ignores.txt # Snyk ignore IDs
├── playwright.config.ts
├── package.json         # Playwright + tooling
└── README.md
```

---

## Local development

### Option A: Docker Compose (recommended)

Bring up **web + app + db** locally using the production-like compose file (adjust image tags if needed, or swap to build context).

```bash
cd deploy
# If you want to build local images first:
docker build -t local/app:dev ../app
docker build -t local/web:dev ../web

# Use overrides to point compose to local images if compose.yml is pinned to registry
IMAGE_REPO_APP=local/app IMAGE_REPO_WEB=local/web TAG=dev docker compose -f compose.yml up -d

# Verify
curl -s http://127.0.0.1:8000/health
curl -I http://127.0.0.1:8081
```

### Option B: Run backend directly

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r app/requirements.txt

# Postgres (local or Docker)
docker run --rm -d --name db -p 5432:5432 \
  -e POSTGRES_DB=supermario -e POSTGRES_USER=mario -e POSTGRES_PASSWORD=secret postgres:15

export DATABASE_URL=postgresql://mario:secret@127.0.0.1:5432/supermario
export PORT=8000
python app/app.py  # dev server

# In another shell, open the frontend from web/static or serve with any static server
```

---

## Testing

### Unit tests (no DB)

```
cd app
pytest -m "not db" -ra
```

### DB tests

```
# ensure Postgres is available as in CI env vars
pytest -m db tests/test_db.py -ra
```

### E2E (Playwright)

```
npm ci
npx playwright install --with-deps
BASE_URL=http://127.0.0.1:8081 npx playwright test
```

### Allure

- Each test job writes Allure results to `allure-results` and JUnit XML.
- CI merges unit+db+e2e and publishes **GitHub Pages** with the latest report.

> Example Pages link configured in CI Slack notification:  
> `https://tainess.github.io/devops-project1/allure/latest/`

---

## CI (PR checks)

Workflow: `.github/workflows/ci.yml`

Jobs:
- **lint** – Pylint over `app/*.py`.
- **unit-tests** – Pytest (non-DB) + Allure, JUnit.
- **db-tests** – Spins up Postgres service; runs DB-only tests + Allure.
- **e2e** – Builds local images, runs 3 containers (db/app/web), Playwright E2E + Allure.
- **build** – Builds images (no push on PR).
- **snyk-pr** – Re-usable workflow from `tAIness/devops-ci-lib` scanning Dockerfiles; uses `security/ignores.txt`.
- **allure-report** – Downloads artifacts, merges Allure results, generates HTML, uploads to **Pages**.
- **deploy-pages** – Publishes the Allure site to GitHub Pages.
- **notify-slack** – Summary with status + Pages URL.

Concurrency, caching (pip/npm), and artifact uploads are enabled.


---

## Release flow

Workflow: `.github/workflows/release.yml`

- **autotag** – On push to `main`, bumps the patch version and creates `vX.Y.Z` tag if none provided.
- **setup** – Resolves `IMAGE_TAG` (`vX.Y.Z` for tags or `sha` fallback).
- **build-and-push-app/web** – Build images, push to **Docker Hub** (if creds provided).  
  Then **mirror each image to Nexus** on the EC2 host using `skopeo` over SSH.
- **snyk-release** – Snyk container test for built images; **fails release** on issues >= threshold.
- **deploy-ec2** – Copies `deploy/compose.yml` + content images to EC2, logs into the selected registry (Hub or Nexus), writes a `.env` with image repos + DB/app variables, pulls the tagged images, and runs `docker compose up -d`.
- **notify-slack** – Status summary.

### Required GitHub Secrets

| Secret | Purpose |
|---|---|
| `DOCKERHUB_USERNAME`, `DOCKERHUB_TOKEN` | Push images to Docker Hub |
| `DOCKERHUB_REPO_APP`, `DOCKERHUB_REPO_WEB` | e.g. `user/supermario-app`, `user/supermario-web` |
| `SNYK_TOKEN` | Snyk auth for image scans |
| `EC2_HOST`, `EC2_USER`, `EC2_SSH_KEY`, `EC2_SSH_PORT` | SSH to EC2 for mirroring/deploy |
| `NEXUS_USERNAME`, `NEXUS_PASSWORD`, `NEXUS_REPO_APP`, `NEXUS_REPO_WEB`, `NEXUS_REGISTRY_DOMAIN` | Mirror images to Nexus |
| `REGISTRY_URL`, `REGISTRY_USERNAME`, `REGISTRY_PASSWORD` | (optional) alt registry login |
| `DEPLOY_REGISTRY` | `hub` (default) or `nexus` |
| `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_PORT` | Compose env for app/db |
| `FLASK_PORT` | App service port (defaults to 8000) |

---

## Configuration

### Backend environment variables

| Var | Default | Notes |
|---|---|---|
| `DATABASE_URL` | `postgresql://supermario:supermario@db:5432/supermario` | Overridden in CI/E2E/EC2 |
| `PORT` | `8000` | Flask/Gunicorn bind |
| `GUNICORN_WORKERS` | `2` | Worker count |
| `DB_POOL_MIN` | `1` | psycopg2 pool min |
| `DB_POOL_MAX` | `10` | psycopg2 pool max |

### Healthcheck

The app container exposes `/health` and the Dockerfile defines a `HEALTHCHECK` that polls it.


---

## Deployment (EC2 quick view)

1. CI builds & pushes images to Docker Hub, then mirrors to **Nexus** on your EC2 host.
2. CI uploads `deploy/compose.yml` and any `content/images/**` to `/srv/supermario/`.
3. CI writes `.env` with image repos/tags and DB/app vars.
4. CI runs:
   ```bash
   docker compose -f compose.yml pull
   docker compose -f compose.yml up -d --no-build
   ```
5. App reachable on `FLASK_PORT` (default 8000), web on port `80` (per compose).

To update manually on EC2:
```bash
cd /srv/supermario
docker compose -f compose.yml pull
docker compose -f compose.yml up -d
```

---

## Security

- Snyk scans on PR and release; ignores are centrally managed in `security/ignores.txt` and translated into `.snyk` during the workflow.
- Containers run as non-root where applicable (`app` sets `USER appuser`).

---

## Troubleshooting

- **App “degraded” health**: DB may not yet be ready; container healthcheck retries. Check `DATABASE_URL` and Postgres logs.
- **Playwright E2E cannot reach services**: verify ports `8000` (app) and `8081` (web) are exposed locally and containers are on the same network.
- **Release failed at Snyk step**: open `snyk-*.json` artifacts to inspect the CVEs; use `security/ignores.txt` judiciously.
- **Nexus mirror errors**: Ensure `skopeo` is installed on EC2 (the workflow installs it if missing) and that the Docker registry is reachable at `127.0.0.1:5000` on the host.


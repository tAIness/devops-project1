# This cell creates a ready-to-use "Mac Release Flow" bundle with scripts and compose file.
# It mirrors the user's GitHub Actions release logic, but for running entirely on a local Mac.
# Files created:
# - Makefile
# - scripts/compute_next_tag.sh
# - scripts/bump_helm_appversion.sh
# - scripts/build_and_push.sh
# - scripts/snyk_scan.sh
# - scripts/run_local.sh
# - .env.local.example
# - deploy/compose.local.yml
# Then it zips them into /mnt/data/mac-release-flow.zip

import os, textwrap, json, zipfile, pathlib

root = "/Users/inesstaef/devops-inc"
scripts_dir = os.path.join(root, "scripts")
deploy_dir = os.path.join(root, "deploy")
os.makedirs(scripts_dir, exist_ok=True)
os.makedirs(deploy_dir, exist_ok=True)

def w(path, content, mode=0o755):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        f.write(content)
    os.chmod(path, mode)

# Makefile
w(os.path.join(root, "Makefile"), textwrap.dedent(r"""
.PHONY: help mac-release compute-tag bump-helm build push snyk run stop logs clean

# Configuration via env or .env.local
# Required: DOCKERHUB_USERNAME, DOCKERHUB_TOKEN, DOCKERHUB_REPO_APP, DOCKERHUB_REPO_WEB
# Optional: TAG (default auto), LOCAL_BUILD=true to use local Dockerfiles instead of pulling
#           FLASK_PORT, DB_*, etc.

help:
	@echo "Targets:"
	@echo "  mac-release     Full flow: compute tag -> bump helm -> build/push -> snyk -> run"
	@echo "  compute-tag     Compute next semver tag (vX.Y.Z) from local git tags"
	@echo "  bump-helm       Update appVersion in all Helm charts + set global.releaseTag"
	@echo "  build           Build images (app/web) and (optionally) push to Docker Hub"
	@echo "  push            Push app/web images to Docker Hub (if not pushed in build)"
	@echo "  snyk            Run Snyk scans on both images (requires SNYK_TOKEN)"
	@echo "  run             Up services via compose.local.yml on your Mac"
	@echo "  stop            Stop compose stack"
	@echo "  logs            Tail compose logs"
	@echo "  clean           Remove containers, images (dangling), and volume"

mac-release: compute-tag bump-helm build snyk run

compute-tag:
	@scripts/compute_next_tag.sh

bump-helm:
	@scripts/bump_helm_appversion.sh

build:
	@scripts/build_and_push.sh build

push:
	@scripts/build_and_push.sh push

snyk:
	@scripts/snyk_scan.sh

run:
	@scripts/run_local.sh up

stop:
	@scripts/run_local.sh down

logs:
	@scripts/run_local.sh logs

clean:
	@scripts/run_local.sh clean
"""), 0o644)

# Scripts
w(os.path.join(scripts_dir, "compute_next_tag.sh"), textwrap.dedent(r"""#!/usr/bin/env bash
set -euo pipefail

# Computes the next tag (vX.Y.Z) from local git tags unless TAG already provided.
# Exports TAG in .env.local for subsequent steps.

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

cd "$ROOT_DIR"

if [[ -n "${TAG:-}" ]]; then
  echo "TAG already provided: $TAG"
else
  if ! command -v git >/dev/null 2>&1; then
    echo "git is required." >&2; exit 1
  fi
  git fetch --tags --force || true
  last="$(git tag -l 'v*.*.*' | sort -V | tail -n1)"
  if [[ -z "$last" ]]; then
    major=0; minor=1; patch=0
  else
    IFS=. read -r vM vN vP <<<"${last#v}"
    major="$vM"; minor="$vN"; patch="$vP"
    patch=$((patch+1))
  fi
  TAG="v${major}.${minor}.${patch}"
  export TAG
fi

echo "TAG=${TAG}"

# Write/merge into .env.local
ENV_FILE=".env.local"
touch "$ENV_FILE"
# Remove existing TAG line, then append
grep -v '^TAG=' "$ENV_FILE" > "${ENV_FILE}.tmp" || true
echo "TAG=${TAG}" >> "${ENV_FILE}.tmp"
mv "${ENV_FILE}.tmp" "$ENV_FILE"

echo "Saved TAG to $ENV_FILE"
"""))

w(os.path.join(scripts_dir, "bump_helm_appversion.sh"), textwrap.dedent(r"""#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

: "${TAG:?TAG must be set (export TAG=... or run make compute-tag)}"

if ! command -v yq >/dev/null 2>&1; then
  echo "yq is required. Install via: brew install yq" >&2
  exit 1
fi

mapfile -t charts < <(git ls-files 'infra/helm/**/Chart.yaml' || true)
if (( ${#charts[@]} == 0 )); then
  echo "No Chart.yaml found under infra/helm"; exit 1
fi

printf 'Charts found:\n%s\n' "${charts[@]}"
for f in "${charts[@]}"; do
  echo "Updating $f to appVersion=${TAG}"
  yq -i '.appVersion = env(TAG)' "$f"
done

if [[ -f "infra/helm/argocd-apps/values.yaml" ]]; then
  echo "Setting global.releaseTag=${TAG} in infra/helm/argocd-apps/values.yaml"
  yq -i '.global.releaseTag = env(TAG)' infra/helm/argocd-apps/values.yaml
else
  echo "infra/helm/argocd-apps/values.yaml not found, skipping releaseTag set."
fi

echo "Helm appVersions updated locally."
"""))

w(os.path.join(scripts_dir, "build_and_push.sh"), textwrap.dedent(r"""#!/usr/bin/env bash
set -euo pipefail

# Usage:
#   scripts/build_and_push.sh build   # build (and push if credentials exist)
#   scripts/build_and_push.sh push    # push only
#
# Required env (in .env.local or exported):
#   TAG
#   DOCKERHUB_USERNAME
#   DOCKERHUB_TOKEN
#   DOCKERHUB_REPO_APP
#   DOCKERHUB_REPO_WEB
#
# Optional:
#   LOCAL_BUILD=true  -> use local Dockerfiles to build images (app/web)
#
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

if [[ -f ".env.local" ]]; then
  set -a; source .env.local; set +a
fi

: "${TAG:?TAG must be set}"
: "${DOCKERHUB_REPO_APP:?}"
: "${DOCKERHUB_REPO_WEB:?}"

ACTION="${1:-build}"

login_registry() {
  if [[ -n "${DOCKERHUB_USERNAME:-}" && -n "${DOCKERHUB_TOKEN:-}" ]]; then
    echo "$DOCKERHUB_TOKEN" | docker login -u "$DOCKERHUB_USERNAME" --password-stdin
  else
    echo "Docker Hub credentials not provided — proceeding without login."
  fi
}

build_images() {
  if [[ "${LOCAL_BUILD:-}" == "true" ]]; then
    echo "Building APP locally: ${DOCKERHUB_REPO_APP}:${TAG}"
    docker build -t "${DOCKERHUB_REPO_APP}:${TAG}" ./app

    echo "Building WEB locally: ${DOCKERHUB_REPO_WEB}:${TAG}"
    docker build -t "${DOCKERHUB_REPO_WEB}:${TAG}" ./web
  else
    echo "LOCAL_BUILD not set — assuming images will be pulled from registry or built in CI."
  fi
}

push_images() {
  if [[ -n "${DOCKERHUB_USERNAME:-}" && -n "${DOCKERHUB_TOKEN:-}" ]]; then
    for IMG in "${DOCKERHUB_REPO_APP}:${TAG}" "${DOCKERHUB_REPO_WEB}:${TAG}"; do
      echo "Pushing $IMG"
      for i in {1..5}; do
        if docker push "$IMG"; then
          echo "Push succeeded: $IMG"; break
        fi
        echo "Push failed (attempt $i). Retrying after $((i*5))s…"
        sleep $((i*5))
        if [[ $i -eq 5 ]]; then echo "Push failed after retries: $IMG" >&2; exit 1; fi
      done
    done
  else
    echo "No Docker Hub credentials — skipping push."
  fi
}

case "$ACTION" in
  build)
    login_registry
    build_images
    push_images
    ;;
  push)
    login_registry
    push_images
    ;;
  *)
    echo "Unknown ACTION: $ACTION" >&2; exit 1
    ;;
esac

echo "Build/push step finished."
"""))

w(os.path.join(scripts_dir, "snyk_scan.sh"), textwrap.dedent(r"""#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

if [[ -f ".env.local" ]]; then
  set -a; source .env.local; set +a
fi

: "${TAG:?TAG must be set}"
: "${DOCKERHUB_REPO_APP:?}"
: "${DOCKERHUB_REPO_WEB:?}"

if ! command -v snyk >/dev/null 2>&1; then
  echo "snyk CLI is required. Install via: brew tap snyk/tap && brew install snyk" >&2
  exit 1
fi

if [[ -z "${SNYK_TOKEN:-}" ]]; then
  echo "SNYK_TOKEN not set — skipping auth and scanning (no-op)."
  exit 0
fi

snyk auth "$SNYK_TOKEN"

images=("{$DOCKERHUB_REPO_APP}:${TAG}" "{$DOCKERHUB_REPO_WEB}:${TAG}")
images=("${DOCKERHUB_REPO_APP}:${TAG}" "${DOCKERHUB_REPO_WEB}:${TAG}")

mkdir -p security
failures=0
for IMG in "${images[@]}"; do
  SAFE="$(echo "$IMG" | tr '/:@' '___')"
  OUT="security/snyk-${SAFE}.json"
  echo "Scanning $IMG"
  set +e
  snyk container test "$IMG" --severity-threshold=high --json-file-output="$OUT"
  rc=$?
  set -e
  if [[ $rc -ne 0 ]]; then
    echo "Snyk found issues for $IMG (rc=$rc)"
    failures=$((failures+1))
  fi
done

if [[ $failures -gt 0 ]]; then
  echo "Snyk reported issues above threshold ($failures image(s)). See ./security/"
  # Do not exit non-zero to avoid blocking local dev; uncomment to enforce
  # exit 1
else
  echo "Snyk scans passed."
fi
"""))

w(os.path.join(scripts_dir, "run_local.sh"), textwrap.dedent(r"""#!/usr/bin/env bash
set -euo pipefail

# Start/stop the local docker compose stack that mirrors EC2 deploy.
# Requires Docker Desktop. Uses deploy/compose.local.yml and .env.local.
# Usage:
#   scripts/run_local.sh up|down|logs|clean

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

if [[ -f ".env.local" ]]; then
  set -a; source .env.local; set +a
fi

COMPOSE_FILE="deploy/compose.local.yml"

cmd="${1:-up}"

case "$cmd" in
  up)
    docker volume create supermario_db_data >/dev/null
    docker compose -f "$COMPOSE_FILE" pull || true
    docker compose -f "$COMPOSE_FILE" up -d --no-build
    echo "App is starting. Try: curl -s http://localhost:${FLASK_PORT:-8000}/health || true"
    ;;
  down)
    docker compose -f "$COMPOSE_FILE" down
    ;;
  logs)
    docker compose -f "$COMPOSE_FILE" logs -f
    ;;
  clean)
    docker compose -f "$COMPOSE_FILE" down -v
    docker image prune -f || true
    ;;
  *)
    echo "Unknown command: $cmd" >&2
    exit 1
    ;;
esac
"""))

# .env.local.example
w(os.path.join(root, ".env.local.example"), textwrap.dedent(r"""# Copy to .env.local and adjust
# Tag will be auto-written by `make compute-tag`
# TAG=v0.1.0

# Docker Hub
DOCKERHUB_USERNAME=your-dockerhub-username
DOCKERHUB_TOKEN=your-dockerhub-token
DOCKERHUB_REPO_APP=docker.io/itaef/supermario-service
DOCKERHUB_REPO_WEB=docker.io/itaef/supermario-front

# Build locally instead of pulling (optional)
# LOCAL_BUILD=true

# Snyk (optional)
# SNYK_TOKEN=xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx

# App config
DB_NAME=mario
DB_USER=mario
DB_PASSWORD=mario123
DB_PORT=5432
FLASK_PORT=8000
"""), 0o644)

# deploy/compose.local.yml
w(os.path.join(deploy_dir, "compose.local.yml"), textwrap.dedent(r"""version: "3.9"

services:
  db:
    image: postgres:15
    container_name: supermario_db
    restart: unless-stopped
    environment:
      POSTGRES_DB: ${DB_NAME:-mario}
      POSTGRES_USER: ${DB_USER:-mario}
      POSTGRES_PASSWORD: ${DB_PASSWORD:-mario123}
    volumes:
      - supermario_db_data:/var/lib/postgresql/data
    ports:
      - "${DB_PORT:-5432}:5432"
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${DB_USER:-mario} -d ${DB_NAME:-mario}"]
      interval: 5s
      timeout: 3s
      retries: 20

  app:
    image: ${DOCKERHUB_REPO_APP}:${TAG}
    container_name: supermario_app
    depends_on:
      db:
        condition: service_healthy
    environment:
      DB_URL: postgresql://${DB_USER:-mario}:${DB_PASSWORD:-mario123}@db:${DB_PORT:-5432}/${DB_NAME:-mario}?sslmode=disable
      FLASK_PORT: ${FLASK_PORT:-8000}
    ports:
      - "${FLASK_PORT:-8000}:8000"
    healthcheck:
      test: ["CMD-SHELL", "curl -fsS http://localhost:${FLASK_PORT:-8000}/health || exit 1"]
      interval: 5s
      timeout: 3s
      retries: 40

  web:
    image: ${DOCKERHUB_REPO_WEB}:${TAG}
    container_name: supermario_web
    depends_on:
      app:
        condition: service_healthy
    environment:
      BACKEND_URL: "http://app:${FLASK_PORT:-8000}"
    ports:
      - "8080:80"

volumes:
  supermario_db_data: {}
"""), 0o644)

# Zip everything
zip_path = "/Users/inesstaef/devops-inc/mac-release-flow.zip"
with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as z:
    for folder, _, files in os.walk(root):
        for f in files:
            full = os.path.join(folder, f)
            z.write(full, arcname=os.path.relpath(full, root))

zip_path

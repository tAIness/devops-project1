#!/usr/bin/env bash
set -euo pipefail

# Anchor at the mac-release-flow folder (where this script lives)
FLOW_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

# Load env from mac-release-flow/.env.local if present
if [[ -f "${FLOW_DIR}/.env.local" ]]; then
  set -a; . "${FLOW_DIR}/.env.local"; set +a
fi

# Resolve the actual Git repo root (so ./app and ./web are found correctly)
REPO_ROOT="$(git -C "${FLOW_DIR}" rev-parse --show-toplevel 2>/dev/null || echo "${FLOW_DIR}")"
cd "${REPO_ROOT}"

# Allow overriding app/web directories (defaults to repo-root/app and repo-root/web)
APP_DIR="${APP_DIR:-${REPO_ROOT}/app}"
WEB_DIR="${WEB_DIR:-${REPO_ROOT}/web}"

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

has_image() {
  docker image inspect "$1" >/dev/null 2>&1
}

build_one() {
  local img="$1" path="$2"
  if [[ ! -d "$path" ]]; then
    echo "ERROR: build path not found: $path" >&2
    exit 1
  fi
  echo "Building $img from $path"
  docker build -t "$img" "$path"
}

build_images() {
  local app_img="${DOCKERHUB_REPO_APP}:${TAG}"
  local web_img="${DOCKERHUB_REPO_WEB}:${TAG}"

  if [[ "${LOCAL_BUILD:-}" == "true" ]]; then
    build_one "$app_img" "$APP_DIR"
    build_one "$web_img" "$WEB_DIR"
  else
    # Auto-build if tag doesn't exist locally
    if has_image "$app_img"; then
      echo "Found local $app_img — skipping build."
    else
      echo "Local $app_img not found — building."
      build_one "$app_img" "$APP_DIR"
    fi
    if has_image "$web_img"; then
      echo "Found local $web_img — skipping build."
    else
      echo "Local $web_img not found — building."
      build_one "$web_img" "$WEB_DIR"
    fi
  fi
}

push_images() {
  if [[ -n "${DOCKERHUB_USERNAME:-}" && -n "${DOCKERHUB_TOKEN:-}" ]]; then
    for IMG in "${DOCKERHUB_REPO_APP}:${TAG}" "${DOCKERHUB_REPO_WEB}:${TAG}"; do
      echo "Pushing $IMG"
      for i in 1 2 3 4 5; do
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

#!/usr/bin/env bash
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

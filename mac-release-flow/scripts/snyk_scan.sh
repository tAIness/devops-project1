#!/usr/bin/env bash
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

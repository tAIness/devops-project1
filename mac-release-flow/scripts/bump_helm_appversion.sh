#!/usr/bin/env bash
set -euo pipefail

# Always anchor at the mac-release-flow folder (where this script lives)
FLOW_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

# Load TAG (and other vars) from the mac-release-flow/.env.local if present
if [[ -f "${FLOW_DIR}/.env.local" ]]; then
  set -a; . "${FLOW_DIR}/.env.local"; set +a
fi

# Now move to the actual Git repo root (so infra/helm/** exists)
REPO_ROOT="$(git -C "${FLOW_DIR}" rev-parse --show-toplevel)"
cd "$REPO_ROOT"

: "${TAG:?TAG must be set (export TAG=... or run make compute-tag)}"

# yq check
if ! command -v yq >/dev/null 2>&1; then
  echo "yq is required. Install via: brew install yq" >&2
  exit 1
fi

# Collect chart files without using mapfile (works on macOS bash 3.2)
charts_file="$(mktemp)"
# Prefer git (only tracked files); fall back to find if needed
if git ls-files 'infra/helm/**/Chart.yaml' >/dev/null 2>&1; then
  git ls-files 'infra/helm/**/Chart.yaml' > "$charts_file"
else
  # fallback: find all Chart.yaml under infra/helm
  find infra/helm -type f -name 'Chart.yaml' > "$charts_file"
fi

if ! [ -s "$charts_file" ]; then
  echo "No Chart.yaml found under infra/helm"; rm -f "$charts_file"; exit 1
fi

echo "Charts found:"
cat "$charts_file"

# Update each Chart.yaml
while IFS= read -r f; do
  [ -z "$f" ] && continue
  echo "Updating $f to appVersion=${TAG}"
  TAG="$TAG" yq -i '.appVersion = env(TAG)' "$f"
done < "$charts_file"

rm -f "$charts_file"

# Update releaseTag if that values.yaml exists
if [[ -f "infra/helm/argocd-apps/values.yaml" ]]; then
  echo "Setting global.releaseTag=${TAG} in infra/helm/argocd-apps/values.yaml"
  TAG="$TAG" yq -i '.global.releaseTag = env(TAG)' infra/helm/argocd-apps/values.yaml
else
  echo "infra/helm/argocd-apps/values.yaml not found, skipping releaseTag set."
fi

echo "Helm appVersions updated locally."

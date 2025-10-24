
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

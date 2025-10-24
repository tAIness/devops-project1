# mac-release-flow (local release & run on Mac)

## One-time
1. `cp mac-release-flow/.env.example mac-release-flow/.env.local` and edit as needed.
2. `brew install yq jq` (if not already installed).
3. `docker login` (if you plan to push images).

## Release locally
```bash
make mac-release     # bumps helm appVersion, builds images, optional push, runs compose

Run only:
docker compose \
  --env-file mac-release-flow/.env.local \
  -f mac-release-flow/deploy/compose.local.yml \
  up -d --no-build

If DB creds change, remove the volume so Postgres re-initializes:
docker compose -f mac-release-flow/deploy/compose.local.yml --env-file mac-release-flow/.env.local down
docker volume rm deploy_supermario_db_data

---

## Why keep this in the repo?
- Repeatable local flow for anyone on the team.
- Shares the same versioned compose + scripts as CI.
- Keeps EC2/CD parts in GitHub Actions, while enabling Mac-only development/deploy locally.

---

## Extra niceties (optional)
- Add a top-level `CONTRIBUTING.md` line: “Copy `.env.example` → `.env.local`”.
- If you want to avoid repo clutter, you can keep the folder as `tools/mac-release/` or `dev/mac/`—it’s purely organizational.





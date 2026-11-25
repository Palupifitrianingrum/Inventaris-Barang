#!/usr/bin/env bash
# Jalankan di root repo (setelah git init / clone). Membuat commit bertahap per komponen.
set -e
commit() { git add "${@:2}" && git commit -m "$1"; }

commit "chore: add gitignore"                          .gitignore
commit "docs: add architecture diagram and docs"       docs README.md 2>/dev/null || true
commit "feat(track-c): add Lambda CRUD function"       track-c-serverless/lambda_function.py
commit "test(track-c): add Lambda test events"         track-c-serverless/events
commit "docs(track-c): add deployment steps"           track-c-serverless/DEPLOY.md
commit "feat(track-a): add Flask CRUD API"             track-a-vm/app.py track-a-vm/requirements.txt
commit "feat(track-a): add schema and connection test" track-a-vm/schema.sql track-a-vm/test_connection.py track-a-vm/.env.example
commit "docs(track-a): add deployment steps"           track-a-vm/DEPLOY.md
commit "feat(track-b): add Dockerfile and API image"   track-b-containers/api
commit "feat(track-b): add docker-compose with 2 services" track-b-containers/docker-compose.yml track-b-containers/.env.example
commit "docs(track-b): add deployment steps"           track-b-containers/DEPLOY.md
echo "Selesai. Jalankan: git push origin main"

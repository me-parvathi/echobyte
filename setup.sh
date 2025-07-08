#!/usr/bin/env bash
set -euo pipefail

# Project root (where this script lives)
ROOT_DIR=$(pwd)

echo "Creating project structure under $ROOT_DIR …"

# Top-level files
touch .gitignore README.md LICENSE docker-compose.yml .env

# Frontend
mkdir -p frontend/{public/assets/{images,videos},src/{api,assets,components,features,hooks,pages,routes,store,styles,utils}}
touch frontend/package.json frontend/vite.config.js
cat > frontend/public/index.html <<'EOF'
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
  <title>React App</title>
</head>
<body>
  <div id="root"></div>
</body>
</html>
EOF
touch frontend/src/{App.jsx,index.jsx}

# Backend
mkdir -p backend/{app/{api/v1/{endpoints,dependencies.py},core,db/{models,base.py,session.py},schemas,services,utils},alembic/versions}
touch backend/requirements.txt backend/Dockerfile backend/app/main.py backend/app/core/{config.py,security.py}
touch backend/app/db/{base.py,session.py}
touch backend/alembic/env.py

# Scripts
mkdir -p scripts
touch scripts/{seed_db.py,manage.py}

# Infra
mkdir -p infra/{terraform}
touch infra/azure-pipelines.yml

# Docs
mkdir -p docs
touch docs/{architecture.md,api-spec.md}

# Tests
mkdir -p tests/{frontend,backend,integration}

echo "All done! 🎉"

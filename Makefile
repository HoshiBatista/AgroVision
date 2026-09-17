UV := uv
NPM := npm
WEB_DIR := apps/web
export PYTHONPATH := src:.

.PHONY: setup web-setup configure prepare demo-data demo-predictions train evaluate model-checksum \
        lint typecheck test db-up db-down migrate seed api web local-init local docker-build \
        docker-up docker-down

setup:
	$(UV) sync --all-groups

web-setup:
	cd $(WEB_DIR) && $(NPM) install

configure:
	$(UV) run python -m scripts.configure_local_env --device mps --database sqlite

# --- Data & ML ---
prepare:
	$(UV) run python -m ml.data.prepare_aerial_sheep

demo-data: prepare
	$(UV) run python -m scripts.make_demo_videos

demo-predictions:
	PYTORCH_ENABLE_MPS_FALLBACK=1 $(UV) run python -m scripts.generate_demo_predictions

train: prepare
	PYTORCH_ENABLE_MPS_FALLBACK=1 $(UV) run python -m ml.training.train_yolo26

evaluate:
	PYTORCH_ENABLE_MPS_FALLBACK=1 $(UV) run python -m ml.evaluation.evaluate_yolo26

model-checksum:
	shasum -a 256 artifacts/training/yolo26n-aerial-sheep-v1/weights/best.pt

# --- Database (requires Docker) ---
db-up:
	docker compose up -d db

db-down:
	docker compose down

migrate:
	$(UV) run alembic upgrade head

seed:
	$(UV) run python -m scripts.seed_demo_user

# --- Quality ---
lint:
	$(UV) run ruff check .
	$(UV) run ruff format --check .

typecheck:
	$(UV) run mypy src apps ml scripts

test:
	$(UV) run pytest

# --- Run ---
api:
	PYTORCH_ENABLE_MPS_FALLBACK=1 $(UV) run uvicorn apps.api.main:app --reload --host 0.0.0.0 --port 8000

web:
	cd $(WEB_DIR) && $(NPM) run dev

local-init: setup web-setup configure migrate seed demo-predictions

local:
	$(UV) run python -m scripts.run_local

# One-shot local bring-up (excluding the long-running api/web servers).
demo: setup db-up migrate seed demo-data
	@echo "Now run 'make api' and 'make web' in separate terminals."

docker-build:
	docker compose build

docker-up:
	docker compose up -d --build

docker-down:
	docker compose down

.PHONY: dev test lint fmt run

dev:
	uv run uvicorn src.app.main:app --reload --host 0.0.0.0 --port 8000

run:
	uv run uvicorn src.app.main:app --host 0.0.0.0 --port 8000

test:
	uv run pytest -q

lint:
	uv run ruff check src tests

fmt:
	uv run ruff format src tests

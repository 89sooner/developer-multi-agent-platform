.PHONY: dev test lint fmt run

dev:
	uvicorn src.app.main:app --reload --host 0.0.0.0 --port 8000

run:
	uvicorn src.app.main:app --host 0.0.0.0 --port 8000

test:
	pytest -q

lint:
	ruff check src tests

fmt:
	ruff format src tests

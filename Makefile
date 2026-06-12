.PHONY: run test lint install clean

run:
	venv/bin/uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

test:
	venv/bin/pytest tests/ -v

lint:
	venv/bin/ruff check app/

install:
	python3 -m venv venv
	venv/bin/pip install -r requirements.txt
	venv/bin/pip install -r requirements-dev.txt

clean:
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

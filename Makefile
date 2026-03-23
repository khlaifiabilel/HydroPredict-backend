.PHONY: install dev run test lint clean docker-build docker-run

# Python environment
VENV := venv
PYTHON := $(VENV)/bin/python
PIP := $(VENV)/bin/pip

# Install dependencies
install:
	python -m venv $(VENV)
	$(PIP) install --upgrade pip
	$(PIP) install -r requirements.txt

# Install development dependencies
dev: install
	$(PIP) install pytest pytest-asyncio httpx black flake8 mypy

# Run the server
run:
	$(PYTHON) run.py

# Run with debug mode
run-debug:
	DEBUG=true $(PYTHON) run.py

# Run tests
test:
	$(PYTHON) -m pytest tests/ -v

# Lint code
lint:
	$(PYTHON) -m flake8 app/
	$(PYTHON) -m mypy app/

# Format code
format:
	$(PYTHON) -m black app/

# Clean up
clean:
	rm -rf $(VENV)
	rm -rf __pycache__
	rm -rf .pytest_cache
	rm -rf .mypy_cache
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

# Docker commands
docker-build:
	docker build -t hydropredict-backend .

docker-run:
	docker run -p 8000:8000 \
		-v $(shell pwd)/../HydroPredict-model:/model:ro \
		hydropredict-backend

docker-compose-up:
	docker-compose up --build

docker-compose-down:
	docker-compose down

# Create .env from example
env:
	cp .env.example .env
	@echo "Created .env file. Please edit with your configuration."

# Show help
help:
	@echo "Available targets:"
	@echo "  install          - Create venv and install dependencies"
	@echo "  dev              - Install with development dependencies"
	@echo "  run              - Run the server"
	@echo "  run-debug        - Run server in debug mode"
	@echo "  test             - Run tests"
	@echo "  lint             - Run linters"
	@echo "  format           - Format code with black"
	@echo "  clean            - Remove virtual environment and cache files"
	@echo "  docker-build     - Build Docker image"
	@echo "  docker-run       - Run Docker container"
	@echo "  docker-compose-up   - Start with docker-compose"
	@echo "  docker-compose-down - Stop docker-compose"
	@echo "  env              - Create .env from example"


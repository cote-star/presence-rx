.PHONY: install test lint run validate clean

UV_ENV := UV_CACHE_DIR=/tmp/uv-cache PYTHONPATH=.

install:
	$(UV_ENV) uv sync --dev

test:
	$(UV_ENV) uv run pytest tests/ -q

lint:
	$(UV_ENV) uv run ruff check presence_rx/ tests/

run:
	$(UV_ENV) uv run presence-rx-run-mvp \
		--generated-dir data/generated \
		--dashboard-dir artifacts/local

validate:
	@for f in data/generated/*.json; do \
		echo "  validating $$f..."; \
		$(UV_ENV) uv run presence-rx-validate "$$f" || exit 1; \
	done
	@echo "All artifacts validated."

clean:
	rm -rf artifacts/local/
	@echo "Cleaned artifacts/local/"

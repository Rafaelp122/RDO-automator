.PHONY: help install run fe test lint lint-backend lint-frontend format check docker-build docker-run clean

# ---------------------------------------------------------------------------
# RDO Automator — Gerador de Diários de Obra
# ---------------------------------------------------------------------------

help:
	@echo "=============================================================================="
	@echo "  RDO Automator v2.0 — Gerador de Diários de Obra"
	@echo "=============================================================================="
	@echo ""
	@echo "📦 SETUP"
	@echo "  make install             - Instala dependências (uv sync + npm install)"
	@echo ""
	@echo "🔥 DESENVOLVIMENTO"
	@echo "  make run                 - Backend em http://localhost:8000 (uvicorn --reload)"
	@echo "  make fe                  - Frontend em http://localhost:3000 (Vite dev server)"
	@echo ""
	@echo "🐳 DOCKER"
	@echo "  make docker-build        - Constrói a imagem Docker do backend"
	@echo "  make docker-run          - Executa o container na porta 8080"
	@echo ""
	@echo "🧪 TESTES & QUALIDADE"
	@echo "  make test                - Roda os 29 testes (unidade + integração)"
	@echo "  make lint                - Ruff + Pyright + tsc (tudo)"
	@echo "  make lint-backend        - Ruff check + Pyright"
	@echo "  make lint-frontend       - tsc --noEmit"
	@echo "  make format              - Ruff format (ordena imports, corrige estilo)"
	@echo "  make check               - test + lint (use antes de commit)"
	@echo ""
	@echo "🧹 MANUTENÇÃO"
	@echo "  make clean               - Remove __pycache__, .pytest_cache, .venv, node_modules, dist"
	@echo ""
	@echo "=============================================================================="

install:
	@echo "=== Backend ==="
	cd backend && uv sync
	@echo ""
	@echo "=== Frontend ==="
	cd frontend && npm install

run:
	cd backend && uv run uvicorn src.main:app --reload --port 8000

fe:
	cd frontend && npm run dev

test:
	cd backend && uv run pytest tests/

lint: lint-backend lint-frontend

lint-backend:
	cd backend && uv run ruff check . tests/
	cd backend && uv run ruff format --check . tests/
	cd backend && uv run pyright src/ --pythonversion 3.11

lint-frontend:
	cd frontend && npx tsc --noEmit

format:
	cd backend && uv run ruff check --fix . tests/
	cd backend && uv run ruff format . tests/

check: test lint

docker-build:
	cd backend && docker build -t rdo-automator .

docker-run:
	docker run -p 8080:8080 --rm rdo-automator

clean:
	@find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name .pytest_cache -exec rm -rf {} + 2>/dev/null || true
	@rm -rf backend/.venv backend/.coverage
	@rm -rf frontend/dist frontend/node_modules

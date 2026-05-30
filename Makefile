.PHONY: help install run fe test lint docker-build docker-run clean

# ---------------------------------------------------------------------------
# RDO Automator — comandos essenciais
# ---------------------------------------------------------------------------

help: ## Exibe esta ajuda
	@grep -E '^[a-zA-Z_-]+:.*?##' $(MAKEFILE_LIST) | sort | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-18s\033[0m %s\n", $$1, $$2}'

install: ## Instala dependências (backend + frontend)
	@echo "=== Backend ==="
	cd backend && uv sync
	@echo ""
	@echo "=== Frontend ==="
	cd frontend && npm install

run: ## Inicia o servidor backend (http://localhost:8000)
	cd backend && uv run uvicorn src.main:app --reload --port 8000

fe: ## Inicia o dev server frontend (http://localhost:3000)
	cd frontend && npm run dev

test: ## Roda todos os testes (unidade + integração)
	cd backend && uv run pytest ../tests/

test-watch: ## Roda os testes automaticamente a cada alteração
	cd backend && uv run pytest-watch ../tests/

lint: ## Typecheck do frontend (TypeScript)
	cd frontend && npx tsc --noEmit

docker-build: ## Constrói a imagem Docker do backend
	cd backend && docker build -t rdo-automator .

docker-run: ## Executa o container (porta 8080)
	docker run -p 8080:8080 --rm rdo-automator

check: test lint ## Roda testes + typecheck (use antes de commit)

clean: ## Remove caches, venv e build artifacts
	@find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name .pytest_cache -exec rm -rf {} + 2>/dev/null || true
	@rm -rf backend/.venv backend/.coverage
	@rm -rf frontend/dist frontend/node_modules

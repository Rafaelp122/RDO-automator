FROM python:3.14-slim
WORKDIR /app
COPY backend/ .
RUN pip install uv && uv sync --frozen --no-dev
CMD ["uv", "run", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]

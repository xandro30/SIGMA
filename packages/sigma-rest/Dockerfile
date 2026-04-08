FROM python:3.13-slim

WORKDIR /app

COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

COPY pyproject.toml uv.lock ./
COPY packages/sigma-core ./packages/sigma-core
COPY packages/sigma-rest ./packages/sigma-rest

RUN uv sync --frozen --no-dev --package sigma-rest

CMD ["uv", "run", "--package", "sigma-rest", "uvicorn", "sigma_rest.main:app", "--host", "0.0.0.0", "--port", "8000"]
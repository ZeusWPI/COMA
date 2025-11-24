FROM ghcr.io/astral-sh/uv:0.9.10-python3.13-trixie-slim AS base


FROM base AS common

RUN export DEBIAN_FRONTEND=noninteractive && \
    apt-get update && \
    apt-get install -y \
        build-essential libglib2.0-dev libpango1.0-dev libpq-dev \
        nodejs npm \
        pandoc

ENV UV_COMPILE_BYTECODE=1
ENV UV_LINK_MODE=copy
ENV UV_TOOL_BIN_DIR=/usr/local/bin

WORKDIR /app

# Install nodejs dependencies
COPY ./package.json package-lock.json ./
RUN npm ci

# Install python dependencies
COPY ./pyproject.toml ./uv.lock ./
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked --no-install-project --no-dev

# Activate the python venv
ENV PATH="/app/.venv/bin:$PATH"


FROM common AS dev

# Also install dev dependencies
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked

CMD ["fastapi", "dev", "--host=0.0.0.0", "--port=80", "--reload", "app/main.py"]


FROM common AS prod

# Build and install our project
COPY ./ ./
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked --no-dev

CMD ["fastapi", "run", "--host=0.0.0.0", "--port=80", "--workers=4", "app/main.py"]

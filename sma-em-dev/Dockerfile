FROM ghcr.io/home-assistant/base-python:3.13-alpine3.22
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

LABEL maintainer="Johann Kellerman <kellerza@gmail.com>"

# Add uv to the `PATH`
ENV PATH="/root/.local/bin/:$PATH"

# Install sma from local source
COPY sma sma

RUN set -x \
    && uv venv \
    && uv pip install --index-strategy unsafe-best-match \
        ./sma
    # && uv sync --frozen --no-dev --all-extras
    # && apk del .build-deps

COPY rootfs /

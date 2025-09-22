ARG BUILD_FROM
FROM ${BUILD_FROM}

LABEL maintainer="Johann Kellerman <kellerza@gmail.com>"

# Add uv to the `PATH`
ENV PATH="/root/.local/bin/:$PATH"

# Install sma from local source
COPY sma sma

RUN set -x \
    # && apk add --no-cache --virtual .build-deps \
    #     build-base \
    && curl -LsSf https://astral.sh/uv/0.8.19/install.sh | sh \
    && uv venv \
    && uv pip install --index-strategy unsafe-best-match \
        ./sma
    # && uv sync --frozen --no-dev --all-extras
    # && apk del .build-deps

COPY rootfs /

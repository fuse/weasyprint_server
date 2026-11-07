FROM debian:12-slim

ARG UV_VERSION=0.8.14
ARG GROUP_ID=1000
ARG USER_ID=1000

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PIP_NO_CACHE_DIR=1
ENV GUNICORN_WORKERS=4
ENV APP_PORT=5000
ENV BASE_URL=http://localhost:5000

RUN apt-get update && apt-get install -y --no-install-recommends \
  python3 \
  ca-certificates \
  tini \
  weasyprint \
  curl && rm -rf /var/lib/apt/lists/*

RUN curl -sSL "https://github.com/astral-sh/uv/releases/download/${UV_VERSION}/uv-x86_64-unknown-linux-gnu.tar.gz" | tar -xz -C /usr/local/bin --strip-components=1

RUN groupadd -g "${GROUP_ID}" app && \
    useradd --create-home --no-log-init -u "${USER_ID}" -g "${GROUP_ID}" app

USER app

WORKDIR /home/app

COPY --chown=app:app src/ src/
COPY --chown=app:app pyproject.toml uv.lock ./

ENV PATH="/home/app/venv/bin:$PATH"
# Versions et empreintes figées par uv.lock : installation vérifiée par hachage, indépendante du cache
RUN uv venv /home/app/venv && \
    . /home/app/venv/bin/activate && \
    uv export --frozen --no-dev --no-emit-project -o /tmp/requirements.txt && \
    uv pip install --require-hashes -r /tmp/requirements.txt && \
    uv pip install --no-deps -e .

ENTRYPOINT ["/usr/bin/tini", "--"]
CMD ["sh", "-c", "gunicorn --workers $GUNICORN_WORKERS --bind 0.0.0.0:$APP_PORT 'src.app:create_app()'"]

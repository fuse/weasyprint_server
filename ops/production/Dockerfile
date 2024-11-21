FROM debian:12-slim

ARG UV_VERSION=0.5.4

ENV PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y --no-install-recommends \
  python3 \
  ca-certificates \
  weasyprint \
  curl && rm -rf /var/lib/apt/lists/*

RUN curl -sSL "https://github.com/astral-sh/uv/releases/download/${UV_VERSION}/uv-x86_64-unknown-linux-gnu.tar.gz" | tar -xz -C /usr/local/bin --strip-components=1

WORKDIR /app

COPY src/ /app/src/
COPY pyproject.toml .

RUN uv pip install -e .

RUN mkdir -p /var/log/weasyprint && chmod 755 /var/log/weasyprint

# Exposition du port
EXPOSE 5000

# Commande de démarrage
CMD ["python3", "-m", "flask", "--app", "src.app:create_app()", "run", "--host=0.0.0.0"]

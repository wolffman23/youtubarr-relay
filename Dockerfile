FROM python:3.13-slim

WORKDIR /app
COPY pyproject.toml README.md LICENSE ./
COPY src ./src
RUN pip install --no-cache-dir . streamlink && useradd --system --uid 10001 relay
USER relay
EXPOSE 8788
CMD ["youtubarr-relay"]

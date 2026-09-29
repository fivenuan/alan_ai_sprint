FROM python:3.13-slim          

WORKDIR /app         

COPY pyproject.toml uv.lock README.md ./
RUN pip install uv && uv sync --frozen --no-dev --no-install-project

COPY src/ ./src/               
COPY data/ ./data/
RUN uv sync --frozen --no-dev
CMD ["uv", "run", "--no-dev", "fetch-urls", "data/urls.txt"]
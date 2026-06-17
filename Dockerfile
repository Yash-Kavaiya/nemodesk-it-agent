# SPDX-License-Identifier: Apache-2.0
FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    NEMODESK_CONFIG=configs/config.yml

WORKDIR /app

# System deps for some langchain/embedding wheels.
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential git curl && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml README.md ./
COPY src ./src
COPY api ./api
COPY configs ./configs
COPY data ./data
COPY eval ./eval

# Install the NemoDesk package (pulls nvidia-nat[langchain] + fastapi).
RUN pip install --upgrade pip && pip install .

EXPOSE 8080

# NVIDIA_API_KEY must be supplied at runtime (-e NVIDIA_API_KEY=...).
HEALTHCHECK --interval=30s --timeout=5s --retries=3 \
    CMD curl -f http://localhost:8080/health || exit 1

CMD ["uvicorn", "api.server:app", "--host", "0.0.0.0", "--port", "8080"]

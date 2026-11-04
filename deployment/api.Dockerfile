ARG PYTHON_IMAGE=python:3.12-slim
FROM ${PYTHON_IMAGE}
WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app/packages/contracts/src:/app/packages/enforcement/src:/app/packages/workspace/src:/app/packages/discovery/src:/app/packages/intelligence/src:/app/packages/funding/src:/app/services/api/src

COPY deployment/api.requirements.txt /tmp/requirements.txt
RUN python -m pip install --no-cache-dir -r /tmp/requirements.txt

COPY pyproject.toml ./
COPY packages ./packages
COPY services ./services
COPY deployment ./deployment

EXPOSE 8000
CMD ["python", "-m", "uvicorn", "nexus_api.main:app", "--host", "0.0.0.0", "--port", "8000"]

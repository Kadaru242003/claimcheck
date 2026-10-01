# Sandbox for running model-written code.
# No network, no host files, limited CPU/memory/processes, non-root user.
FROM python:3.12-slim
RUN pip install --no-cache-dir "pytest==8.3.5" && useradd --create-home runner
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
USER runner
WORKDIR /work

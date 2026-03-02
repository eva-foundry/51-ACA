# Dockerfile: Epic 15 Sync Orchestration Job
# Build: Azure DevOps Pipeline in main repo
# Push: marcosandacr20260203.azurecr.io/epic15-sync:latest
# Run: Azure Container Apps Job

FROM mcr.microsoft.com/powershell:lts-ubuntu-22.04

# Metadata
LABEL description="Epic 15 Data Model Sync Orchestrator (Tier 2: Resilient Execution)"
LABEL version="1.0.0"
LABEL maintainer="ACA Platform Team"

# Set environment variables
ENV PYTHONIOENCODING=utf-8 \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH="/root/.local/bin:${PATH}"

# Install dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    wget \
    git \
    jq \
    python3.12 \
    python3.12-venv \
    python3-pip \
    python3.12-dev \
    build-essential \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install Azure CLI
RUN curl -sL https://aka.ms/InstallAzureCLIDeb | bash

# Create Python virtual environment and install packages
RUN python3.12 -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Upgrade pip
RUN /opt/venv/bin/pip install --upgrade pip setuptools wheel

# Install Python dependencies (Agent Framework, Azure SDK, etc.)
COPY --chown=root:root requirements.txt /tmp/requirements.txt
RUN /opt/venv/bin/pip install --no-cache-dir -r /tmp/requirements.txt

# Create working directory
WORKDIR /app

# Copy orchestration scripts
COPY --chown=root:root ./scripts/ /app/scripts/
COPY --chown=root:root ./config/ /app/config/

# Create state directories
RUN mkdir -p /app/state/checkpoints \
    && mkdir -p /app/state/rollback \
    && mkdir -p /app/logs \
    && chmod -R 755 /app/state /app/logs

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD pwsh -Command "if (Test-Path '/app/state/health-check.ok') { exit 0 } else { exit 1 }"

# Entrypoint
ENTRYPOINT [ "pwsh", "-NoProfile", "-Command" ]
CMD [ "/app/scripts/sync-orchestration-job.ps1" ]

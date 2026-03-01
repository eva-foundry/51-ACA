# Sprint Agent Docker Image
# Purpose: Pre-built environment for GitHub Actions sprint execution
# Image: ghcr.io/eva-foundry/51-aca-sprint-agent:latest
# Size: ~600MB (Python 3.12 slim + dependencies)
# Startup: 30 sec (vs 5 min for pip install in runner)

FROM python:3.12-slim

LABEL org.opencontainers.image.title="ACA Sprint Agent"
LABEL org.opencontainers.image.description="EVA Factory DPDCA orchestration agent for 51-ACA"
LABEL org.opencontainers.image.authors="eva-foundry"
LABEL org.opencontainers.image.source="https://github.com/eva-foundry/51-ACA"

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    curl \
    jq \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Install GitHub CLI (for issue management in workflow)
RUN curl -fsSL https://cli.github.com/packages/githubcli-archive-keyring.gpg | gpg --dearmor -o /usr/share/keyrings/githubcli-archive-keyring.gpg \
    && echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" | tee /etc/apt/sources.list.d/github-cli.sources > /dev/null \
    && apt-get update && apt-get install -y gh && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /workspace

# Copy requirements and install Python dependencies
COPY services/api/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt \
    && pip install --no-cache-dir \
    openai \
    ruff \
    pytest \
    pytest-asyncio \
    httpx

# Copy repository files (minimal - only what sprint agent needs)
COPY .github/scripts/sprint_agent.py .github/scripts/
COPY PLAN.md STATUS.md README.md ./
COPY .eva .eva
COPY services services

# Create non-root user for security
RUN useradd -m -u 1000 agent && chown -R agent:agent /workspace
USER agent

# Default command: print version info
CMD ["python3", "--version"]

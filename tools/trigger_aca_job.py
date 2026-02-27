"""
tools/trigger_aca_job.py
========================
Implements the `trigger_aca_job` tool referenced by:
  collection-agent.yaml  (job_name: aca-51-collector)
  analysis-agent.yaml    (job_name: aca-51-analysis)
  generation-agent.yaml  (job_name: aca-51-delivery)

Triggers an Azure Container Apps Job execution via azure-mgmt-appcontainers SDK.

Required environment variables:
  AZURE_SUBSCRIPTION_ID  - Azure subscription containing the ACA environment
  ACA_RESOURCE_GROUP     - Resource group (e.g. aca-prod-rg for Phase 2,
                           or marco-sandbox-rg for Phase 1)
  ACA_ACA_ENVIRONMENT    - Container Apps Environment name (e.g. aca-51-env)

Credential: DefaultAzureCredential (Managed Identity in production,
            WorkloadIdentity via OIDC in GitHub Actions).

Phase 1 stub mode: if AZURE_SUBSCRIPTION_ID is not set, the trigger is
logged and a dry-run JobExecutionResult is returned so the pipeline can be
tested end-to-end without real Azure resources.
"""
from __future__ import annotations

import logging
import os
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import List

__all__ = ["trigger_aca_job", "JobExecutionResult"]

logger = logging.getLogger(__name__)

_SUBSCRIPTION_ID = os.getenv("AZURE_SUBSCRIPTION_ID", "")
_RESOURCE_GROUP = os.getenv("ACA_RESOURCE_GROUP", "")
_ACA_ENV = os.getenv("ACA_ACA_ENVIRONMENT", "")


@dataclass
class JobExecutionResult:
    ok: bool
    job_name: str
    execution_id: str = ""
    dry_run: bool = False
    error: str = ""
    env_args: List[str] = field(default_factory=list)


def trigger_aca_job(
    job_name: str,
    env_args: List[str] | None = None,
) -> JobExecutionResult:
    """
    Trigger a Container App Job execution.

    Args:
        job_name:  Name of the Container App Job (e.g. "aca-51-collector").
        env_args:  List of CLI-style key-value pairs injected as environment
                   variable overrides, e.g. ["--scan-id", "abc", "--subscription-id", "xyz"].
                   These are passed as JobExecutionTemplate environment variables.

    Returns:
        JobExecutionResult with ok=True and execution_id on success.
    """
    env_args = env_args or []

    if not _SUBSCRIPTION_ID:
        # Phase 1 / local dev stub
        stub_id = f"dry-run-{uuid.uuid4().hex[:8]}"
        logger.warning(
            "trigger_aca_job: AZURE_SUBSCRIPTION_ID not set -- dry-run mode. "
            "job=%s execution_id=%s args=%s",
            job_name, stub_id, env_args,
        )
        return JobExecutionResult(
            ok=True,
            job_name=job_name,
            execution_id=stub_id,
            dry_run=True,
            env_args=env_args,
        )

    try:
        from azure.identity import DefaultAzureCredential
        from azure.mgmt.appcontainers import ContainerAppsAPIClient
        from azure.mgmt.appcontainers.models import (
            JobExecutionTemplate,
            JobExecutionContainer,
            EnvironmentVar,
        )
    except ImportError as exc:
        return JobExecutionResult(
            ok=False,
            job_name=job_name,
            error=(
                f"azure-mgmt-appcontainers not installed: {exc}. "
                "Run: pip install azure-mgmt-appcontainers"
            ),
        )

    # Convert ["--scan-id", "abc", "--subscription-id", "xyz"] ->
    # [EnvironmentVar(name="ARG_0", value="--scan-id"), ...]
    env_vars = [
        EnvironmentVar(name=f"ARG_{i}", value=v)
        for i, v in enumerate(env_args)
    ]

    try:
        credential = DefaultAzureCredential()
        client = ContainerAppsAPIClient(credential, _SUBSCRIPTION_ID)
        result = client.jobs.begin_start(
            resource_group_name=_RESOURCE_GROUP,
            job_name=job_name,
            template=JobExecutionTemplate(containers=[
                JobExecutionContainer(name=job_name, env=env_vars)
            ]),
        ).result()
        execution_id = result.name or f"exec-{uuid.uuid4().hex[:8]}"
        logger.info(
            "trigger_aca_job: triggered job=%s execution_id=%s", job_name, execution_id
        )
        return JobExecutionResult(
            ok=True,
            job_name=job_name,
            execution_id=execution_id,
            env_args=env_args,
        )
    except Exception as exc:  # noqa: BLE001
        logger.error("trigger_aca_job: failed job=%s error=%s", job_name, exc)
        return JobExecutionResult(ok=False, job_name=job_name, error=str(exc))

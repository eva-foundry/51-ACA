"""
# EVA-STORY: ACA-07-006
# EVA-STORY: ACA-07-021
DeliverablePackager -- ZIP, SHA-256 sign, upload to Azure Blob Storage.
Returns a 7-day (168-hour) SAS URL for the client to download.
"""
from __future__ import annotations
import hashlib
import io
import json
import logging
import zipfile
from datetime import datetime, timedelta, timezone

from azure.storage.blob import BlobServiceClient, BlobSasPermissions, generate_blob_sas
from azure.identity import DefaultAzureCredential

logger = logging.getLogger(__name__)
SAS_HOURS = 168  # 7 days per 08-payment.md spec


class DeliverablePackager:
    def __init__(self, storage_account: str, container_name: str, account_key: str) -> None:
        self.storage_account = storage_account
        self.container_name = container_name
        self.account_key = account_key
        account_url = f"https://{storage_account}.blob.core.windows.net"
        self.client = BlobServiceClient(
            account_url=account_url,
            credential=DefaultAzureCredential(),
        )

    def package_and_upload(
        self,
        scan_id: str,
        subscription_id: str,
        findings: list[dict],
        artifacts: list[dict],
    ) -> str:
        """Build a zip, upload, return SAS URL."""
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, mode="w", compression=zipfile.ZIP_DEFLATED) as zf:
            # findings manifest
            zf.writestr(
                "findings.json",
                json.dumps(findings, indent=2, ensure_ascii=True),
            )
            # IaC templates
            for artifact in artifacts:
                folder = artifact["template_id"]
                for f in artifact.get("files", []):
                    zf.writestr(f"{folder}/{f['name']}", f["content"])

        zip_bytes = zip_buffer.getvalue()
        sha256 = hashlib.sha256(zip_bytes).hexdigest()
        blob_name = f"{scan_id}/{scan_id}-deliverable.zip"

        # upload
        container_client = self.client.get_container_client(self.container_name)
        container_client.upload_blob(
            name=blob_name,
            data=zip_bytes,
            overwrite=True,
            metadata={"sha256": sha256, "subscriptionId": subscription_id},
        )
        logger.info("[%s] uploaded %d bytes sha256=%s", scan_id, len(zip_bytes), sha256[:16])

        # SAS -- generate_blob_sas requires the storage account key; managed identity
        # cannot sign SAS tokens. Pass ACA_STORAGE_ACCOUNT_KEY from env.
        expiry = datetime.now(timezone.utc) + timedelta(hours=SAS_HOURS)
        sas_token = generate_blob_sas(
            account_name=self.storage_account,
            container_name=self.container_name,
            blob_name=blob_name,
            account_key=self.account_key,
            permission=BlobSasPermissions(read=True),
            expiry=expiry,
        )
        return (
            f"https://{self.storage_account}.blob.core.windows.net"
            f"/{self.container_name}/{blob_name}?{sas_token}"
        )

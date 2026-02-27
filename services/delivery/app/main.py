"""
Delivery service -- CLI entry.
Packages analysis findings into a deliverable zip with IaC templates.
Usage: python -m app.main --scan-id SCAN --subscription-id SUB
"""
from __future__ import annotations
import argparse
import logging
import sys
import os

from app.generator import TemplateGenerator
from app.packager import DeliverablePackager

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s")
logger = logging.getLogger("delivery")


def _get_cosmos():
    from app.cosmos import CosmosHelper
    return CosmosHelper(
        url=os.environ["COSMOS_URL"],
        key=os.environ["COSMOS_KEY"],
        database=os.environ.get("COSMOS_DATABASE", "aca-db"),
    )


def main(scan_id: str, subscription_id: str) -> None:
    logger.info("[%s] delivery started", scan_id)
    cosmos = _get_cosmos()

    # 1. Load findings for this scan
    findings = list(cosmos.query_items(
        "findings",
        f"SELECT * FROM c WHERE c.scanId = '{scan_id}'",
        subscription_id=subscription_id,
    ))

    if not findings:
        logger.error("[%s] no findings found -- aborting delivery", scan_id)
        sys.exit(1)

    logger.info("[%s] loaded %d findings", scan_id, len(findings))

    # 2. Generate IaC templates for each finding
    generator = TemplateGenerator()
    artifacts = generator.generate(findings, scan_id=scan_id, subscription_id=subscription_id)
    logger.info("[%s] generated %d IaC artifacts", scan_id, len(artifacts))

    # 3. Package into a zip and upload to Blob Storage
    packager = DeliverablePackager(
        storage_account=os.environ["STORAGE_ACCOUNT"],
        container_name=os.environ.get("DELIVERY_CONTAINER", "deliverables"),
    )
    sas_url = packager.package_and_upload(
        scan_id=scan_id,
        subscription_id=subscription_id,
        findings=findings,
        artifacts=artifacts,
    )
    logger.info("[%s] deliverable available at: %s", scan_id, sas_url)

    # 4. Write deliverable record to Cosmos
    cosmos.upsert_item("deliverables", {
        "id": f"del-{scan_id}",
        "scanId": scan_id,
        "subscriptionId": subscription_id,
        "sasUrl": sas_url,
        "findingCount": len(findings),
        "artifactCount": len(artifacts),
    }, subscription_id=subscription_id)
    logger.info("[%s] delivery complete", scan_id)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="51-ACA Delivery Packager")
    parser.add_argument("--scan-id", required=True)
    parser.add_argument("--subscription-id", required=True)
    args = parser.parse_args()
    main(args.scan_id, args.subscription_id)

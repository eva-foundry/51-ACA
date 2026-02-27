"""
FindingsAssembler -- load collected data + persist findings to Cosmos.
"""
from __future__ import annotations
import logging
from datetime import datetime, timezone

logger = logging.getLogger(__name__)


class FindingsAssembler:
    def __init__(self, scan_id: str, subscription_id: str, cosmos_client) -> None:
        self.scan_id = scan_id
        self.subscription_id = subscription_id
        self.cosmos = cosmos_client

    # ------------------------------------------------------------------
    # Data loading
    # ------------------------------------------------------------------
    def load_collected_data(self) -> dict:
        """
        Reads inventories, cost-data, advisor, and network containers
        for this scan and merges into the dict structure consumed by rules.
        """
        pk = self.subscription_id
        data: dict = {
            "resources": [],
            "cost_rows": [],
            "advisor_recommendations": [],
            "policy_states": [],
            "network_topology": {},
        }

        # inventory
        try:
            inventory_items = list(self.cosmos.query_items(
                "inventories",
                f"SELECT * FROM c WHERE c.scanId = '{self.scan_id}'",
                subscription_id=pk,
            ))
            for item in inventory_items:
                data["resources"].extend(item.get("resources", []))
        except Exception as exc:
            logger.warning("[%s] inventory load failed: %s", self.scan_id, exc)

        # cost data
        try:
            cost_items = list(self.cosmos.query_items(
                "cost-data",
                f"SELECT * FROM c WHERE c.scanId = '{self.scan_id}'",
                subscription_id=pk,
            ))
            for item in cost_items:
                data["cost_rows"].extend(item.get("rows", []))
        except Exception as exc:
            logger.warning("[%s] cost-data load failed: %s", self.scan_id, exc)

        # advisor
        try:
            advisor_items = list(self.cosmos.query_items(
                "advisor",
                f"SELECT * FROM c WHERE c.scanId = '{self.scan_id}'",
                subscription_id=pk,
            ))
            for item in advisor_items:
                data["advisor_recommendations"].extend(item.get("recommendations", []))
        except Exception as exc:
            logger.warning("[%s] advisor load failed: %s", self.scan_id, exc)

        logger.info(
            "[%s] collected data loaded: %d resources, %d cost rows, %d advisor recs",
            self.scan_id,
            len(data["resources"]),
            len(data["cost_rows"]),
            len(data["advisor_recommendations"]),
        )
        return data

    # ------------------------------------------------------------------
    # Persistence
    # ------------------------------------------------------------------
    def save_findings(self, findings: list[dict]) -> None:
        """Upsert each finding to the findings container (pk=subscriptionId)."""
        for finding in findings:
            doc = {
                **finding,
                "scanId": self.scan_id,
                "subscriptionId": self.subscription_id,
                "generatedAt": datetime.now(timezone.utc).isoformat(),
            }
            self.cosmos.upsert_item("findings", doc, subscription_id=self.subscription_id)
        logger.info("[%s] saved %d findings", self.scan_id, len(findings))

    def mark_analysis_complete(self, count: int) -> None:
        """Update the scan record: status='complete', findingCount=count."""
        try:
            scan = self.cosmos.get_item("scans", self.scan_id, subscription_id=self.subscription_id)
            scan["status"] = "complete"
            scan["findingCount"] = count
            scan["completedAt"] = datetime.now(timezone.utc).isoformat()
            self.cosmos.upsert_item("scans", scan, subscription_id=self.subscription_id)
            logger.info("[%s] scan marked complete, %d findings", self.scan_id, count)
        except Exception as exc:
            logger.error("[%s] failed to mark scan complete: %s", self.scan_id, exc)

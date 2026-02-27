"""
# EVA-STORY: ACA-02-014
ACA Collector -- Service 1
Runs as an Azure Container App Job (triggered per scan).

Entry point: python -m app.main --scan-id <id> --subscription-id <sub>

Collects:
  1. Resource inventory (Resource Graph)
  2. Cost Management -- 91 days daily granularity
  3. Azure Advisor recommendations
  4. Policy compliance state
  5. Network topology signals (NSG, public IPs, private DNS, VNet)
"""
import argparse
import os
import sys
from datetime import datetime, timezone

from app.preflight import run_preflight
from app.azure_client import AzureCollector
from app.ingest import Ingestor


def main() -> int:
    parser = argparse.ArgumentParser(description="ACA Collector")
    parser.add_argument("--scan-id", required=True)
    parser.add_argument("--subscription-id", required=True)
    parser.add_argument("--preflight-only", action="store_true",
                        help="Run preflight checks only, do not collect")
    args = parser.parse_args()

    scan_id = args.scan_id
    sub_id = args.subscription_id

    print(f"[INFO] ACA Collector starting | scan={scan_id} sub={sub_id}")

    # Step 1: Pre-flight permission validation
    pf = run_preflight(sub_id)
    if pf["verdict"] == "FAIL":
        print(f"[FAIL] Pre-flight failed: {pf['blockers']}")
        return 1
    if pf["verdict"] == "PASS_WITH_WARNINGS":
        for w in pf.get("warnings", []):
            print(f"[WARN] {w}")

    if args.preflight_only:
        print(f"[PASS] Pre-flight OK | verdict={pf['verdict']}")
        return 0

    # Step 2: Collect
    collector = AzureCollector(subscription_id=sub_id)
    ingestor = Ingestor(scan_id=scan_id, subscription_id=sub_id)

    print("[INFO] Collecting resource inventory...")
    resources = collector.get_inventory()
    ingestor.save_inventory(resources)
    print(f"[INFO] Inventory: {len(resources)} resources saved")

    print("[INFO] Collecting cost data (91 days)...")
    cost_rows = collector.get_cost_data(days=91)
    ingestor.save_cost_data(cost_rows)
    print(f"[INFO] Cost: {len(cost_rows)} daily rows saved")

    print("[INFO] Collecting Azure Advisor recommendations...")
    advisor = collector.get_advisor_recommendations()
    ingestor.save_advisor(advisor)
    print(f"[INFO] Advisor: {len(advisor)} recommendations saved")

    print("[INFO] Collecting policy compliance state...")
    policy = collector.get_policy_state()
    ingestor.save_policy(policy)
    print(f"[INFO] Policy: {policy.get('total', 0)} policy states saved")

    print("[INFO] Collecting network topology signals...")
    network = collector.get_network_topology()
    ingestor.save_network(network)
    print("[INFO] Network topology saved")

    ingestor.mark_collection_complete()
    print(f"[PASS] Collection complete | scan={scan_id}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

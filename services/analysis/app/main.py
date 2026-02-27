"""
# EVA-STORY: ACA-03-004
ACA Analysis Engine -- Service 2
Runs as an Azure Container App Job (triggered after collection completes).

Entry point: python -m app.main --scan-id <id> --subscription-id <sub>

Runs 12 rule-based heuristics + 29-foundry AI agents.
Writes findings JSON to Cosmos findings container.
"""
import argparse
import os
import sys

from app.rules import ALL_RULES
from app.findings import FindingsAssembler


def main() -> int:
    parser = argparse.ArgumentParser(description="ACA Analysis Engine")
    parser.add_argument("--scan-id", required=True)
    parser.add_argument("--subscription-id", required=True)
    args = parser.parse_args()

    scan_id = args.scan_id
    sub_id = args.subscription_id

    print(f"[INFO] ACA Analysis Engine starting | scan={scan_id} sub={sub_id}")

    assembler = FindingsAssembler(scan_id=scan_id, subscription_id=sub_id)
    data = assembler.load_collected_data()

    if not data:
        print("[FAIL] No collected data found in Cosmos for this scan")
        return 1

    findings = []
    for rule in ALL_RULES:
        try:
            result = rule(data)
            if result:
                findings.extend(result if isinstance(result, list) else [result])
                print(f"[INFO] Rule {rule.__name__}: {len(result) if isinstance(result, list) else 1} finding(s)")
        except Exception as e:
            print(f"[WARN] Rule {rule.__name__} failed: {e}")

    print(f"[INFO] Rules produced {len(findings)} findings")

    # TODO: run 29-foundry analysis-agent and redteam-agent for beyond-rule findings
    # agent_findings = run_analysis_agent(data, findings)
    # findings.extend(agent_findings)

    assembler.save_findings(findings)
    assembler.mark_analysis_complete(len(findings))
    print(f"[PASS] Analysis complete | findings={len(findings)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

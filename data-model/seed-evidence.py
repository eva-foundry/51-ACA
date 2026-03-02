#!/usr/bin/env python3
# EVA-STORY: ACA-12-022
# Seed evidence layer from .eva/evidence/*.json files
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import db

repo_root = Path(__file__).parent.parent
result = db.seed_evidence(repo_root, actor="seed:evidence")

print(f"[INFO] Imported: {result['imported']}")
print(f"[INFO] Skipped:  {result['skipped']}")
if result['errors']:
    print(f"[WARN] Errors:   {len(result['errors'])}")
    for err in result['errors']:
        print(f"  - {err}")
else:
    print("[PASS] No errors")

print(f"[INFO] Total evidence records: {db.total_active()}")
print(f"[INFO] Evidence layer count: {db.count_all().get('evidence', 0)}")

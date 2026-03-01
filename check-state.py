#!/usr/bin/env python3
"""Simple state check that writes JSON output"""
import sys
import json
from pathlib import Path

sys.path.insert(0, 'data-model')
import db

results = {}

# CHECK 1: LOCAL DB
try:
    s2 = [s for s in db.list_layer('wbs') if s.get('sprint_id') == 'Sprint-02']
    results['local_db'] = {
        'count': len(s2),
        'expected': 15,
        'pass': len(s2) == 15,
        'story_ids': [s.get('id') for s in s2][:5]  # First 5
    }
except Exception as e:
    results['local_db'] = {'error': str(e), 'pass': False}

# CHECK 2: Cloud Model (via requests)
try:
    import requests
    url = "https://marco-eva-data-model.livelyflower-7990bc7b.canadacentral.azurecontainerapps.io/model/projects/51-ACA"
    resp = requests.get(url, timeout=5)
    proj = resp.json()
    results['cloud_model'] = {
        'ado_project': proj.get('ado_project'),
        'expected': '51-aca',
        'pass': proj.get('ado_project') == '51-aca',
        'maturity': proj.get('maturity'),
        'phase': proj.get('phase')
    }
except Exception as e:
    results['cloud_model'] = {'error': str(e), 'pass': False}

# CHECK 3: Workflow Files
wf_yml = Path('.github/workflows/sprint-agent.yml').exists()
wf_py = Path('.github/scripts/sprint_agent.py').exists()
results['workflow_files'] = {
    'yml': wf_yml,
    'py': wf_py,
    'pass': wf_yml and wf_py
}

# Write results
output_file = 'state-check-results.json'
with open(output_file, 'w') as f:
    json.dump(results, f, indent=2)

print(f"[PASS] Results written to {output_file}")

# Print summary
print("\n=== QUICK SUMMARY ===")
for check, data in results.items():
    status = "PASS" if data.get('pass') else "FAIL"
    print(f"{check:20s}: {status}")

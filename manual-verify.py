#!/usr/bin/env python3
"""
Manual Verification Script - Run this directly
Implements user's log file pattern suggestion
"""
import sys
import subprocess
from pathlib import Path
from datetime import datetime

# Setup
sys.path.insert(0, 'data-model')
import db

log_file = f"verify-{datetime.now().strftime('%Y%m%d-%H%M%S')}.log"
results = {"pass": 0, "fail": 0}

def log(msg, level="INFO"):
    """Write to both console and log file"""
    print(f"[{level}] {msg}")
    with open(log_file, 'a', encoding='utf-8') as f:
        f.write(f"[{level}] {msg}\n")

# Header
log("=" * 50, "INFO")
log("SPRINT 2 VERIFICATION (Log File Pattern)", "INFO")
log(f"Time: {datetime.now()}", "INFO")
log(f"Log: {log_file}", "INFO")
log("=" * 50, "INFO")
log("", "INFO")

# CHECK 1: LOCAL DB
log("CHECK 1: LOCAL DB Sprint 2 Linkage", "INFO")
log("-" * 40, "INFO")
try:
    s2 = [s for s in db.list_layer('wbs') if s.get('sprint_id') == 'Sprint-02']
    count = len(s2)
    story_ids = [s.get('id') for s in s2[:5]]
    
    log(f"Stories linked: {count}", "INFO")
    log(f"Expected: 15", "INFO")
    log(f"Sample IDs: {story_ids}", "INFO")
    
    if count == 15:
        log("Result: PASS", "PASS")
        results["pass"] += 1
    else:
        log("Result: FAIL", "FAIL")
        results["fail"] += 1
except Exception as e:
    log(f"Result: ERROR - {e}", "FAIL")
    results["fail"] += 1

log("", "INFO")

# CHECK 2: ADO Sprint 2 Assignment
log("CHECK 2: ADO Sprint 2 Assignment (3 samples)", "INFO")
log("-" * 40, "INFO")

samples = [2978, 2985, 2993]
ado_pass = 0

for wi_id in samples:
    try:
        result = subprocess.run(
            ['az', 'boards', 'work-item', 'show', '--id', str(wi_id),
             '--org', 'https://dev.azure.com/marcopresta',
             '--query', 'fields."System.IterationPath"', '-o', 'tsv'],
            capture_output=True, text=True, timeout=10
        )
        
        iteration = result.stdout.strip()
        expected = "51-aca\\Sprint 2"
        
        if iteration == expected:
            log(f"WI {wi_id}: {iteration} [PASS]", "PASS")
            ado_pass += 1
        else:
            log(f"WI {wi_id}: {iteration} [FAIL - expected '{expected}']", "FAIL")
    except Exception as e:
        log(f"WI {wi_id}: ERROR - {e}", "FAIL")

if ado_pass == 3:
    log("Result: PASS (3/3 correct)", "PASS")
    results["pass"] += 1
else:
    log(f"Result: FAIL ({ado_pass}/3 correct)", "FAIL")
    results["fail"] += 1

log("", "INFO")

# CHECK 3: Baseline Tests
log("CHECK 3: Baseline Test Suite", "INFO")
log("-" * 40, "INFO")
log("Running: pytest services/ -x -q --tb=line", "INFO")

try:
    result = subprocess.run(
        [sys.executable, '-m', 'pytest', 'services/', '-x', '-q', '--tb=line'],
        capture_output=True, text=True, timeout=60
    )
    
    exit_code = result.returncode
    output_lines = result.stdout.split('\n')
    
    log(f"Exit Code: {exit_code}", "INFO")
    
    # Log last 10 lines
    for line in output_lines[-10:]:
        if line.strip():
            log(f"  {line}", "INFO")
    
    if exit_code == 0:
        log("Result: PASS", "PASS")
        results["pass"] += 1
    else:
        log("Result: FAIL", "FAIL")
        results["fail"] += 1
        
except Exception as e:
    log(f"Result: ERROR - {e}", "FAIL")
    results["fail"] += 1

log("", "INFO")

# SUMMARY
log("=" * 50, "INFO")
log("FINAL RESULT", "INFO")
log("=" * 50, "INFO")
log(f"PASS: {results['pass']} / 3", "PASS" if results['fail'] == 0 else "INFO")
log(f"FAIL: {results['fail']} / 3", "FAIL" if results['fail'] > 0 else "INFO")
log("", "INFO")

if results['fail'] == 0:
    log("STATUS: READY FOR SPRINT 2 EXECUTION", "PASS")
    log("", "INFO")
    log("Next Steps:", "INFO")
    log("1. Create GitHub issue with Sprint 2 manifest", "INFO")
    log("2. Add label: sprint-task", "INFO")
    log("3. Monitor: GitHub Actions", "INFO")
else:
    log("STATUS: NOT READY - FIX FAILURES ABOVE", "FAIL")
    log("", "INFO")
    log("Next Steps:", "INFO")
    log("- Review VERIFICATION-REPORT.md", "INFO")
    log("- Fix failed checks above", "INFO")

log("", "INFO")
log(f"Full results saved to: {log_file}", "INFO")

print(f"\n[INFO] Results written to: {log_file}")
print(f"[INFO] Read with: type {log_file}")

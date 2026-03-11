# EVA-STORY: ACA-12-022
# Seed evidence layer from .eva/evidence/*.json files
param(
    [switch]$DryRun
)

$ErrorActionPreference = "Stop"

Write-Host "[INFO] Seeding evidence layer from .eva/evidence/*.json"

if ($DryRun) {
    Write-Host "[INFO] DRY-RUN mode -- no database writes"
}

$script = @'
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
'@

if ($DryRun) {
    Write-Host "[INFO] Would run:"
    Write-Host $script
} else {
    $script | Set-Content "$env:TEMP\seed-evidence.py" -Encoding UTF8
    C:\eva-foundry\.venv\Scripts\python.exe "$env:TEMP\seed-evidence.py"
}

Write-Host "[INFO] Done"

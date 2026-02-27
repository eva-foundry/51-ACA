<!-- SPRINT_MANIFEST
{
  "sprint_id": "SPRINT-00",
  "sprint_title": "Pre-flight: 3 blocking bugs",
  "target_branch": "sprint/00-preflight",
  "epic": "ACA-00",
  "stories": [
    {
      "id": "ACA-06-021",
      "title": "Delete duplicate checkout router block (lines 349-402)",
      "wbs": "6.0.1",
      "epic": "Epic 06 -- Billing",
      "files_to_create": [
        "services/api/app/routers/checkout.py"
      ],
      "acceptance": [
        "services/api/app/routers/checkout.py has exactly one 'from fastapi import APIRouter' line",
        "services/api/app/routers/checkout.py has exactly one 'router = APIRouter' line",
        "File imports without error: python3 -c \"from services.api.app.routers.checkout import router\"",
        "POST /v1/checkout/tier2 and POST /v1/checkout/tier3 and POST /v1/checkout/webhook endpoints each appear exactly once",
        "GET /entitlements appears exactly once"
      ],
      "implementation_notes": "The file services/api/app/routers/checkout.py currently has 402 lines. Lines 1-348 are the correct, complete implementation. Lines 349-402 are an accidental duplicate block starting with 'from fastapi import APIRouter, HTTPException, Request' followed by a second 'router = APIRouter(tags=[\"checkout\"])' and duplicate stubs for tier2/tier3/webhook/entitlements. This causes a FastAPI route registration conflict that breaks all billing endpoints at runtime. Fix: rewrite the file keeping lines 1-348 exactly as-is and REMOVING lines 349-402 entirely. The file must end after line 348 (the return statement in get_entitlements). READ the current file content first, then output the corrected version with lines 349-402 removed. Do NOT alter any content in lines 1-348. The EVA-STORY tag is already present at line 1 or 2 -- do not duplicate it."
    },
    {
      "id": "ACA-03-021",
      "title": "Fix FindingsAssembler instantiation -- add missing cosmos_client",
      "wbs": "3.0.1",
      "epic": "Epic 03 -- Analysis",
      "files_to_create": [
        "services/analysis/app/main.py"
      ],
      "acceptance": [
        "services/analysis/app/main.py imports CosmosClient from azure.cosmos",
        "FindingsAssembler is called with cosmos_client as third argument",
        "CosmosClient is initialized from os.environ.get('ACA_COSMOS_URL', '')",
        "File imports without error when ACA_COSMOS_URL is absent (lazy init, no crash on import)",
        "python3 -c \"import sys; sys.path.insert(0,'services/analysis'); from app.main import main\" exits without AttributeError"
      ],
      "implementation_notes": "The file services/analysis/app/main.py line 29 calls FindingsAssembler(scan_id=scan_id, subscription_id=sub_id) but the FindingsAssembler.__init__ signature in services/analysis/app/findings.py is def __init__(self, scan_id: str, subscription_id: str, cosmos_client) -> None -- the third argument cosmos_client is REQUIRED and missing. This causes a TypeError at runtime the moment analysis tries to run. Fix: in main.py, add the following after the existing imports: 'from azure.cosmos import CosmosClient as _CosmosClient' and add a helper function _get_cosmos_client() that reads ACA_COSMOS_URL = os.environ.get('ACA_COSMOS_URL', '') and if ACA_COSMOS_URL is empty returns None (graceful degradation for CI), else returns _CosmosClient(url=ACA_COSMOS_URL, credential=...) using DefaultAzureCredential from azure.identity. Then change line 29 to: 'assembler = FindingsAssembler(scan_id=scan_id, subscription_id=sub_id, cosmos_client=_get_cosmos_client())'. The file is only 61 lines -- rewrite it in full keeping the existing logic and adding only the minimal CosmosClient wiring. EVA-STORY tag ACA-03-004 is already on line 2 -- keep it, do not add ACA-03-021 as a second tag on the same file."
    },
    {
      "id": "ACA-07-021",
      "title": "Fix packager.py: SAS_HOURS=168 and user_delegation_key SAS generation",
      "wbs": "7.0.1",
      "epic": "Epic 07 -- Delivery",
      "files_to_create": [
        "services/delivery/app/packager.py"
      ],
      "acceptance": [
        "SAS_HOURS = 168 (not 24)",
        "Module-level docstring says '7-day SAS URL' (not '24-hour')",
        "generate_blob_sas is called with user_delegation_key parameter (not account_key or credential)",
        "get_user_delegation_key is called on self.client before generate_blob_sas",
        "generate_blob_sas call has NO account_key parameter and NO credential parameter",
        "File imports without error"
      ],
      "implementation_notes": "The file services/delivery/app/packager.py has two bugs. Bug 1: line 18 sets SAS_HOURS = 24 but per docs/12-IaCscript.md the SAS expiry MUST be 168 hours (7 days). Change to SAS_HOURS = 168. Also update the module docstring on line 4 from '24-hour SAS URL' to '7-day SAS URL'. Bug 2: lines 68-76 call generate_blob_sas(account_name=..., container_name=..., blob_name=..., account_key=None, credential=DefaultAzureCredential(), permission=..., expiry=...). This is invalid -- generate_blob_sas does not accept a 'credential' parameter and passing account_key=None produces an unsigned SAS token. The correct Entra-based pattern is: first call udk = self.client.get_user_delegation_key(key_start_time=datetime.now(timezone.utc), key_expiry_time=expiry) then call generate_blob_sas(account_name=self.storage_account, container_name=self.container_name, blob_name=blob_name, user_delegation_key=udk, permission=BlobSasPermissions(read=True), expiry=expiry). Remove the azure.identity import if DefaultAzureCredential is no longer used elsewhere in the file (it is used in __init__ -- keep it). Rewrite the file in full: 81 lines currently. Keep all existing logic except apply the two fixes. EVA-STORY tag ACA-07-006 is on line 2 -- keep it."
    }
  ]
}
-->

## Sprint 00: Pre-flight Bug Fixes

**Type**: Bug fix sprint -- 3 blocking defects
**Branch**: sprint/00-preflight
**Trigger**: sprint-task label

### Summary

Three bugs discovered during Sonnet review (issue #6) that block production operation:

| ID | File | Bug | Impact |
|---|---|---|---|
| ACA-06-021 | services/api/app/routers/checkout.py | Duplicate APIRouter block lines 349-402 | All billing endpoints broken at startup |
| ACA-03-021 | services/analysis/app/main.py | FindingsAssembler missing cosmos_client arg | TypeError when analysis job runs |
| ACA-07-021 | services/delivery/app/packager.py | SAS_HOURS=24, invalid generate_blob_sas call | Deliverables expire in 24h, SAS token unsigned |

### Definition of Done

- [ ] Each file has exactly one definition of each route/class
- [ ] ruff check services/ exits 0
- [ ] pytest services/ --co -q exits 0
- [ ] No duplicate APIRouter registrations in checkout.py
- [ ] FindingsAssembler called with cosmos_client in analysis/main.py
- [ ] SAS_HOURS=168 in packager.py
- [ ] user_delegation_key used in generate_blob_sas

### Dependencies

None -- all three fixes are independent file edits.

### Notes

These are the ACA-06-021/ACA-03-021/ACA-07-021 stories from the pre-flight sprint
added to PLAN.md in the session summary above. ACA-12-021 and ACA-12-022 are already DONE.

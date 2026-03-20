Absolutely — here is a more implementation-heavy version you can hand to Copilot. It adds a suggested repo layout, Python interfaces, API shapes, job orchestration flow, and starter FastAPI stubs aligned to your ACA architecture and plan. The structure matches your current repo direction with `services/api`, `services/collector`, `services/analysis`, `services/delivery`, and Cosmos containers partitioned by `subscriptionId`.



---



\## `COPILOT\_CONTEXT\_ACA\_COLLECTOR.md`



````md

\# COPILOT\_CONTEXT\_ACA\_COLLECTOR.md



\## Mission



Build the ACA \*\*pre-flight + Azure data collector subsystem\*\*.



This subsystem must:



\- authenticate against client Azure subscriptions using supported connection modes

\- verify effective read-only permissions before collection

\- determine \*\*extraction depth\*\*

\- collect subscription data using read-only Azure APIs

\- write normalized results to ACA-owned Cosmos containers

\- expose progress and status APIs

\- never write to the client subscription



ACA is a \*\*read-only Azure Cost Advisor SaaS\*\*.

Clients review findings and deploy generated scripts themselves.

ACA does not mutate client Azure resources.



---



\## Architecture Alignment



ACA architecture already assumes:



\- multi-tenant Microsoft identity support

\- FastAPI API service

\- Azure Container Apps / Container App Jobs

\- Cosmos DB with strict tenant isolation by `subscriptionId`

\- collector job for Azure reads

\- analysis job for 12 rules

\- delivery job for script packaging



Collection scope currently includes:



\- Azure Resource Graph

\- Cost Management Query API (91 days, daily rows)

\- Azure Advisor API

\- Azure Policy Insights

\- network topology via ARM reads

\- optional Activity Logs / Log Analytics signals



---



\## Supported Connection Modes



Implement the collector/auth flow so all of these are possible:



\### Mode A — Delegated sign-in

Use Microsoft identity sign-in (`authority=common`).

Good for trials and easy onboarding.



\### Mode B — Client-provided service principal

Enterprise-friendly.

ACA receives credentials / secret reference and uses that identity.



\### Mode C — Azure Lighthouse delegation

MSP-style model.

ACA uses delegated access to client subscriptions.



All modes must feed the same \*\*pre-flight capability probe\*\* and the same collector orchestration logic.



---



\## Core Rule



ACA must remain \*\*strictly read-only\*\* toward the client subscription.



Never:



\- create resources in the client tenant

\- modify client resources

\- change RBAC

\- deploy agents into the client subscription

\- execute remediation inside the client subscription



ACA may only:



\- read data from the client subscription

\- write data into ACA-owned Cosmos DB / Blob Storage / internal services



---



\## Repo Layout To Generate / Complete



Recommended structure:



services/

&nbsp; api/

&nbsp;   app/

&nbsp;     main.py

&nbsp;     config.py

&nbsp;     dependencies.py

&nbsp;     clients/

&nbsp;       arm\_client\_factory.py

&nbsp;       resource\_graph\_client.py

&nbsp;       cost\_mgmt\_client.py

&nbsp;       advisor\_client.py

&nbsp;       policy\_client.py

&nbsp;       activity\_client.py

&nbsp;     models/

&nbsp;       preflight.py

&nbsp;       scans.py

&nbsp;       collection.py

&nbsp;       common.py

&nbsp;     routes/

&nbsp;       health.py

&nbsp;       auth.py

&nbsp;       preflight.py

&nbsp;       collect.py

&nbsp;       scans.py

&nbsp;     services/

&nbsp;       preflight\_service.py

&nbsp;       scan\_service.py

&nbsp;       entitlement\_service.py

&nbsp;     repos/

&nbsp;       scans\_repo.py

&nbsp;       inventories\_repo.py

&nbsp;       cost\_data\_repo.py

&nbsp;       advisor\_repo.py

&nbsp;       findings\_repo.py

&nbsp;       clients\_repo.py



&nbsp; collector/

&nbsp;   app/

&nbsp;     main.py

&nbsp;     orchestrator.py

&nbsp;     job\_context.py

&nbsp;     collectors/

&nbsp;       inventory.py

&nbsp;       cost.py

&nbsp;       advisor.py

&nbsp;       policy.py

&nbsp;       network.py

&nbsp;       activity.py

&nbsp;     normalizers/

&nbsp;       inventory\_normalizer.py

&nbsp;       cost\_normalizer.py

&nbsp;       advisor\_normalizer.py

&nbsp;     writers/

&nbsp;       cosmos\_writer.py

&nbsp;     probes/

&nbsp;       auth\_probe.py

&nbsp;       resource\_graph\_probe.py

&nbsp;       reader\_probe.py

&nbsp;       cost\_probe.py

&nbsp;       advisor\_probe.py

&nbsp;       policy\_probe.py

&nbsp;       activity\_probe.py

&nbsp;     utils/

&nbsp;       retry.py

&nbsp;       paging.py

&nbsp;       logging.py



shared/

&nbsp; contracts/

&nbsp;   preflight\_contract.py

&nbsp;   collector\_contract.py

&nbsp;   scan\_contract.py



tests/

&nbsp; unit/

&nbsp;   test\_preflight\_service.py

&nbsp;   test\_resource\_graph\_probe.py

&nbsp;   test\_cost\_probe.py

&nbsp;   test\_inventory\_collector.py

&nbsp;   test\_cost\_collector.py

&nbsp;   test\_advisor\_collector.py

&nbsp; integration/

&nbsp;   test\_preflight\_api.py

&nbsp;   test\_collect\_api.py



This aligns with the repo shape already described in ACA docs and keeps API, collector, and contracts cleanly separated.



---



\## Data Stores



Cosmos containers already expected:



\- `scans`

\- `inventories`

\- `cost-data`

\- `advisor`

\- later `findings`

\- later `deliverables`



RULE:

Every tenant read/write MUST use:



\- `partition\_key = subscriptionId`



No cross-tenant queries.



---



\## Pre-flight Design



\### Purpose



Pre-flight is a \*\*capability and extraction-depth assessment\*\*, not just an auth check.



It must answer:



\- Can ACA authenticate?

\- What can ACA read?

\- What cannot ACA read?

\- Can ACA proceed?

\- What findings will be limited if it proceeds?



\### Top-level result



Use:



\- `PASS`

\- `PASS\_WITH\_WARNINGS`

\- `FAIL`



\### Probe result statuses



Use:



\- `PASS`

\- `WARN`

\- `FAIL`

\- `SKIP`



\### Mandatory probes



1\. ARM auth token acquired

2\. Resource Graph query works

3\. Subscription Reader / inventory read works

4\. Cost Management query works

5\. Azure Advisor read works

6\. 91-day cost window available



\### Optional probes



7\. Policy Insights available

8\. Activity / Log Analytics available

9\. Network topology reads available



---



\## Extraction Depth Model



Pre-flight must compute one of:



\- `DEPTH\_0\_NONE`

\- `DEPTH\_1\_INVENTORY\_ONLY`

\- `DEPTH\_2\_INVENTORY\_COST`

\- `DEPTH\_3\_STANDARD`

\- `DEPTH\_4\_ENHANCED`

\- `DEPTH\_5\_ACTIVITY\_ENHANCED`



Interpretation:



\### DEPTH\_0\_NONE

No useful extraction possible.



\### DEPTH\_1\_INVENTORY\_ONLY

Can read inventory only.

No useful FinOps scan beyond inventory observations.



\### DEPTH\_2\_INVENTORY\_COST

Can read inventory and cost.

Can produce basic cost-oriented analysis.



\### DEPTH\_3\_STANDARD

Can read inventory + cost + Advisor.

This is the minimum strong ACA scan.



\### DEPTH\_4\_ENHANCED

Standard plus policy and network signals.



\### DEPTH\_5\_ACTIVITY\_ENHANCED

Enhanced plus activity / idle detection sources.



Store extraction depth in the scan record and return it to the UI.



---



\## Pre-flight Response Contract



Suggested Pydantic model:



```python

from pydantic import BaseModel

from typing import List, Optional, Literal



ProbeStatus = Literal\["PASS", "WARN", "FAIL", "SKIP"]

PreflightTopStatus = Literal\["PASS", "PASS\_WITH\_WARNINGS", "FAIL"]



class ProbeResult(BaseModel):

&nbsp;   probe\_name: str

&nbsp;   status: ProbeStatus

&nbsp;   scope\_tested: Optional\[str] = None

&nbsp;   required\_role\_or\_permission: Optional\[str] = None

&nbsp;   actual\_result: str

&nbsp;   error\_code: Optional\[str] = None

&nbsp;   human\_guidance: Optional\[str] = None

&nbsp;   can\_continue\_without\_this: bool = False

&nbsp;   collection\_impact: Optional\[str] = None



class ExtractionDepthResult(BaseModel):

&nbsp;   level: Literal\[

&nbsp;       "DEPTH\_0\_NONE",

&nbsp;       "DEPTH\_1\_INVENTORY\_ONLY",

&nbsp;       "DEPTH\_2\_INVENTORY\_COST",

&nbsp;       "DEPTH\_3\_STANDARD",

&nbsp;       "DEPTH\_4\_ENHANCED",

&nbsp;       "DEPTH\_5\_ACTIVITY\_ENHANCED",

&nbsp;   ]

&nbsp;   rationale: str



class PreflightResponse(BaseModel):

&nbsp;   scan\_id: str

&nbsp;   subscription\_id: str

&nbsp;   tenant\_id: Optional\[str] = None

&nbsp;   status: PreflightTopStatus

&nbsp;   extraction\_depth: ExtractionDepthResult

&nbsp;   probes: List\[ProbeResult]

&nbsp;   summary: str

````



---



\## Collector Design



\### Collector responsibilities



After successful pre-flight, the collector:



1\. creates / updates scan state

2\. pulls subscription inventory

3\. pulls 91 days of cost data

4\. pulls Advisor recommendations

5\. optionally pulls policy / network / activity signals

6\. writes normalized rows to Cosmos

7\. updates scan stats

8\. marks scan as succeeded or failed

9\. optionally triggers analysis



\### Collection status flow



Recommended statuses:



\* `queued`

\* `running`

\* `preflight\_failed`

\* `preflight\_warn`

\* `collected`

\* `succeeded`

\* `failed`



\### Required scan stats



\* `inventoryCount`

\* `costRows`

\* `advisorRecs`

\* `policySignalsCount`

\* `networkSignalsCount`

\* `warningsCount`

\* `errorsCount`



---



\## Source Collector Interfaces



Use a common collector contract.



```python

from typing import Protocol, Any, Dict, List



class Collector(Protocol):

&nbsp;   async def collect(self, ctx: "JobContext") -> Dict\[str, Any]:

&nbsp;       ...

```



\### Job context



```python

from pydantic import BaseModel

from typing import Optional, Literal



class JobContext(BaseModel):

&nbsp;   scan\_id: str

&nbsp;   subscription\_id: str

&nbsp;   tenant\_id: Optional\[str] = None

&nbsp;   auth\_mode: Literal\["delegated", "service\_principal", "lighthouse"]

&nbsp;   extraction\_depth: str

&nbsp;   actor\_id: str

```



---



\## Suggested Collector Modules



\### `collectors/inventory.py`



Source:



\* Azure Resource Graph



Responsibilities:



\* query all resources in subscription

\* normalize fields:



&nbsp; \* subscriptionId

&nbsp; \* resourceId

&nbsp; \* type

&nbsp; \* name

&nbsp; \* resourceGroup

&nbsp; \* location

&nbsp; \* sku

&nbsp; \* tags

\* write to `inventories`



\### `collectors/cost.py`



Source:



\* Cost Management Query API



Responsibilities:



\* query 91 days of daily data

\* handle pagination

\* handle 429 with exponential backoff

\* normalize fields:



&nbsp; \* date

&nbsp; \* MeterCategory

&nbsp; \* MeterName

&nbsp; \* resourceGroup

&nbsp; \* resourceId (hashed if required)

&nbsp; \* PreTaxCost

&nbsp; \* currency

\* write to `cost-data`



\### `collectors/advisor.py`



Source:



\* Azure Advisor API



Responsibilities:



\* collect all recommendation categories

\* normalize important fields

\* preserve raw JSON

\* write to `advisor`



\### `collectors/policy.py`



Source:



\* Azure Policy Insights



Responsibilities:



\* collect compliance summary

\* write optional signal set into scan or future container



\### `collectors/network.py`



Source:



\* ARM reads



Responsibilities:



\* gather light topology signals:



&nbsp; \* NSG rule counts

&nbsp; \* public IP count

&nbsp; \* private DNS zone count

&nbsp; \* VNet peering map



\### `collectors/activity.py`



Source:



\* Activity Logs / Log Analytics



Responsibilities:



\* optional only

\* strengthen:



&nbsp; \* ghost resource detection

&nbsp; \* idle detection

&nbsp; \* night shutdown opportunity detection



---



\## Retry / Paging Utilities



\### `utils/retry.py`



Implement exponential backoff for:



\* 429

\* transient 5xx errors

\* selected Azure SDK retryable failures



\### `utils/paging.py`



Implement helpers for:



\* nextLink paging

\* continuation token paging

\* batch writes to Cosmos



---



\## API Endpoints To Implement



\### POST `/v1/auth/preflight`



Purpose:



\* run capability probes only

\* persist scan + preflight result

\* return detailed result to UI



Request example:



```json

{

&nbsp; "subscriptionId": "xxxx-xxxx-xxxx",

&nbsp; "mode": "delegated"

}

```



Response:



\* `PreflightResponse`



\### GET `/v1/preflight/{scan\_id}`



Purpose:



\* retrieve previous pre-flight result



---



\### POST `/v1/collect/start`



Purpose:



\* validate pre-flight success

\* create scan if needed

\* trigger collector Container App Job

\* return scan handle



Request example:



```json

{

&nbsp; "scanId": "scan\_123",

&nbsp; "subscriptionId": "xxxx-xxxx-xxxx"

}

```



Response example:



```json

{

&nbsp; "scanId": "scan\_123",

&nbsp; "status": "queued"

}

```



\### GET `/v1/collect/status/{scan\_id}`



Purpose:



\* frontend polling endpoint

\* returns current lifecycle state and counters



---



\## Starter FastAPI Route Stubs



\### `routes/preflight.py`



```python

from fastapi import APIRouter, Depends, HTTPException

from app.models.preflight import PreflightResponse

from app.services.preflight\_service import PreflightService



router = APIRouter(prefix="/v1/auth", tags=\["auth"])



@router.post("/preflight", response\_model=PreflightResponse)

async def run\_preflight(

&nbsp;   payload: dict,

&nbsp;   svc: PreflightService = Depends(),

) -> PreflightResponse:

&nbsp;   return await svc.run(payload)



@router.get("/preflight/{scan\_id}", response\_model=PreflightResponse)

async def get\_preflight(

&nbsp;   scan\_id: str,

&nbsp;   svc: PreflightService = Depends(),

) -> PreflightResponse:

&nbsp;   result = await svc.get(scan\_id)

&nbsp;   if not result:

&nbsp;       raise HTTPException(status\_code=404, detail="Preflight result not found")

&nbsp;   return result

```



\### `routes/collect.py`



```python

from fastapi import APIRouter, Depends, HTTPException

from app.services.scan\_service import ScanService



router = APIRouter(prefix="/v1/collect", tags=\["collect"])



@router.post("/start")

async def start\_collection(

&nbsp;   payload: dict,

&nbsp;   svc: ScanService = Depends(),

):

&nbsp;   return await svc.start\_collection(payload)



@router.get("/status/{scan\_id}")

async def get\_collection\_status(

&nbsp;   scan\_id: str,

&nbsp;   svc: ScanService = Depends(),

):

&nbsp;   result = await svc.get\_status(scan\_id)

&nbsp;   if not result:

&nbsp;       raise HTTPException(status\_code=404, detail="Scan not found")

&nbsp;   return result

```



---



\## PreflightService Responsibilities



Suggested methods:



```python

class PreflightService:

&nbsp;   async def run(self, payload: dict) -> PreflightResponse: ...

&nbsp;   async def get(self, scan\_id: str) -> PreflightResponse | None: ...

&nbsp;   async def \_probe\_auth(self, ...): ...

&nbsp;   async def \_probe\_resource\_graph(self, ...): ...

&nbsp;   async def \_probe\_reader(self, ...): ...

&nbsp;   async def \_probe\_cost\_management(self, ...): ...

&nbsp;   async def \_probe\_advisor(self, ...): ...

&nbsp;   async def \_probe\_policy(self, ...): ...

&nbsp;   async def \_probe\_activity(self, ...): ...

&nbsp;   async def \_compute\_extraction\_depth(self, probes: list\[ProbeResult]) -> ExtractionDepthResult: ...

```



---



\## ScanService Responsibilities



Suggested methods:



```python

class ScanService:

&nbsp;   async def start\_collection(self, payload: dict) -> dict: ...

&nbsp;   async def get\_status(self, scan\_id: str) -> dict | None: ...

&nbsp;   async def trigger\_collector\_job(self, scan\_id: str) -> None: ...

```



`trigger\_collector\_job()` should call Azure Container Apps Job start APIs or your selected job trigger mechanism. The plan already calls for collector job orchestration and later automatic analysis triggering after collection.



---



\## Cosmos Repository Contracts



\### `repos/scans\_repo.py`



```python

class ScansRepo:

&nbsp;   async def create\_scan(self, doc: dict) -> dict: ...

&nbsp;   async def get\_scan(self, scan\_id: str, subscription\_id: str) -> dict | None: ...

&nbsp;   async def upsert\_preflight\_result(self, subscription\_id: str, doc: dict) -> None: ...

&nbsp;   async def update\_status(self, subscription\_id: str, scan\_id: str, status: str, \*\*stats) -> None: ...

```



\### `repos/inventories\_repo.py`



```python

class InventoriesRepo:

&nbsp;   async def bulk\_upsert(self, subscription\_id: str, docs: list\[dict]) -> int: ...

```



\### `repos/cost\_data\_repo.py`



```python

class CostDataRepo:

&nbsp;   async def bulk\_upsert(self, subscription\_id: str, docs: list\[dict]) -> int: ...

```



\### `repos/advisor\_repo.py`



```python

class AdvisorRepo:

&nbsp;   async def bulk\_upsert(self, subscription\_id: str, docs: list\[dict]) -> int: ...

```



---



\## Collector Orchestrator Pseudocode



```python

async def run\_collection(ctx: JobContext):

&nbsp;   await scans\_repo.update\_status(ctx.subscription\_id, ctx.scan\_id, "running")



&nbsp;   stats = {

&nbsp;       "inventoryCount": 0,

&nbsp;       "costRows": 0,

&nbsp;       "advisorRecs": 0,

&nbsp;       "policySignalsCount": 0,

&nbsp;       "networkSignalsCount": 0,

&nbsp;       "warningsCount": 0,

&nbsp;       "errorsCount": 0,

&nbsp;   }



&nbsp;   try:

&nbsp;       inventory\_docs = await inventory\_collector.collect(ctx)

&nbsp;       stats\["inventoryCount"] = len(inventory\_docs)



&nbsp;       if ctx.extraction\_depth in {"DEPTH\_2\_INVENTORY\_COST", "DEPTH\_3\_STANDARD", "DEPTH\_4\_ENHANCED", "DEPTH\_5\_ACTIVITY\_ENHANCED"}:

&nbsp;           cost\_docs = await cost\_collector.collect(ctx)

&nbsp;           stats\["costRows"] = len(cost\_docs)



&nbsp;       if ctx.extraction\_depth in {"DEPTH\_3\_STANDARD", "DEPTH\_4\_ENHANCED", "DEPTH\_5\_ACTIVITY\_ENHANCED"}:

&nbsp;           advisor\_docs = await advisor\_collector.collect(ctx)

&nbsp;           stats\["advisorRecs"] = len(advisor\_docs)



&nbsp;       if ctx.extraction\_depth in {"DEPTH\_4\_ENHANCED", "DEPTH\_5\_ACTIVITY\_ENHANCED"}:

&nbsp;           policy\_stats = await policy\_collector.collect(ctx)

&nbsp;           network\_stats = await network\_collector.collect(ctx)



&nbsp;       if ctx.extraction\_depth == "DEPTH\_5\_ACTIVITY\_ENHANCED":

&nbsp;           await activity\_collector.collect(ctx)



&nbsp;       await scans\_repo.update\_status(ctx.subscription\_id, ctx.scan\_id, "collected", \*\*stats)



&nbsp;       # optional analysis trigger

&nbsp;       await maybe\_trigger\_analysis(ctx)



&nbsp;       await scans\_repo.update\_status(ctx.subscription\_id, ctx.scan\_id, "succeeded", \*\*stats)



&nbsp;   except Exception as ex:

&nbsp;       stats\["errorsCount"] += 1

&nbsp;       await scans\_repo.update\_status(

&nbsp;           ctx.subscription\_id,

&nbsp;           ctx.scan\_id,

&nbsp;           "failed",

&nbsp;           error=str(ex),

&nbsp;           \*\*stats,

&nbsp;       )

&nbsp;       raise

```



---



\## Error handling rules



\### Fatal pre-flight failures



Fail with explicit customer guidance when:



\* no ARM token

\* no Reader access

\* no Resource Graph

\* no Cost Management Reader

\* no usable cost window for a standard scan



\### Warning-only conditions



Proceed with warnings when:



\* Policy Insights unavailable

\* Log Analytics unavailable

\* some topology reads unavailable



\### Retry logic



For Azure API `429`:



\* exponential backoff

\* bounded retries

\* warning persisted in scan record if degraded



---



\## UI expectations



Frontend should be able to show:



\### Pre-flight checklist



\* green / yellow / red rows

\* extraction depth label

\* clear “can proceed / cannot proceed” message



\### Collection progress



\* resource count discovered

\* cost rows collected

\* advisor rec count

\* elapsed time

\* final scan status



This matches your current onboarding and scan-progress design.



---



\## Testing expectations



\### Unit tests



\* probe success / fail / warn cases

\* extraction depth calculation

\* cost pagination and retry

\* inventory normalization

\* advisor normalization

\* scan status lifecycle



\### Integration tests



\* `POST /v1/auth/preflight`

\* `POST /v1/collect/start`

\* `GET /v1/collect/status/{scan\_id}`



Target plan already includes pre-flight probe UX, inventory under 60s for modest subscription size, 91-day cost extraction, Advisor/policy/network collection, and scan lifecycle updates.



---



\## Short implementation summary for Copilot



Build a read-only ACA subsystem that:



\* supports delegated / service principal / Lighthouse connection modes

\* probes Azure access before collection

\* computes extraction depth

\* collects inventory, 91-day cost, Advisor, and optional policy/network/activity data

\* writes normalized tenant-isolated data into Cosmos

\* exposes pre-flight and collection APIs

\* supports Container App Job execution

\* never modifies the client subscription

\* prepares data for the 12-rule ACA analysis engine



```



A couple of implementation notes worth keeping in mind as you hand this to Copilot: your ACA docs already lock in the three connection modes, the collector job, the Cosmos container names, the `partition\_key=subscriptionId` rule, the five baseline probes, and the 91-day Cost Management extraction scope, so this prompt stays consistent with what you already defined. 



The bigger architectural fit is also good: your live EVA model exposes self-describing layer metadata and a 12-domain ontology over 87 operational layers, with the execution-engine layers L52–L75 still planned, so ACA can use the current operational model now while later plugging richer execution telemetry back into EVA as those future layers come online. 



If you want the next step, I’d make it the \*\*actual starter code pack\*\*: FastAPI models, route files, repo interfaces, and collector class skeletons in Python.

```




Here’s the \*\*starter code pack\*\* for the ACA pre-flight + collector subsystem.



\## `services/api/app/models/preflight.py`



```python

from \_\_future\_\_ import annotations



from typing import List, Literal, Optional



from pydantic import BaseModel, Field





ProbeStatus = Literal\["PASS", "WARN", "FAIL", "SKIP"]

PreflightTopStatus = Literal\["PASS", "PASS\_WITH\_WARNINGS", "FAIL"]

ExtractionDepth = Literal\[

&nbsp;   "DEPTH\_0\_NONE",

&nbsp;   "DEPTH\_1\_INVENTORY\_ONLY",

&nbsp;   "DEPTH\_2\_INVENTORY\_COST",

&nbsp;   "DEPTH\_3\_STANDARD",

&nbsp;   "DEPTH\_4\_ENHANCED",

&nbsp;   "DEPTH\_5\_ACTIVITY\_ENHANCED",

]





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

&nbsp;   level: ExtractionDepth

&nbsp;   rationale: str





class PreflightRequest(BaseModel):

&nbsp;   subscriptionId: str = Field(..., min\_length=1)

&nbsp;   mode: Literal\["delegated", "service\_principal", "lighthouse"] = "delegated"

&nbsp;   tenantId: Optional\[str] = None





class PreflightResponse(BaseModel):

&nbsp;   scan\_id: str

&nbsp;   subscription\_id: str

&nbsp;   tenant\_id: Optional\[str] = None

&nbsp;   status: PreflightTopStatus

&nbsp;   extraction\_depth: ExtractionDepthResult

&nbsp;   probes: List\[ProbeResult]

&nbsp;   summary: str

```



---



\## `services/api/app/models/scans.py`



```python

from \_\_future\_\_ import annotations



from typing import Literal, Optional



from pydantic import BaseModel





ScanStatus = Literal\[

&nbsp;   "queued",

&nbsp;   "running",

&nbsp;   "preflight\_failed",

&nbsp;   "preflight\_warn",

&nbsp;   "collected",

&nbsp;   "succeeded",

&nbsp;   "failed",

]





class StartCollectionRequest(BaseModel):

&nbsp;   scanId: str

&nbsp;   subscriptionId: str





class ScanStatusResponse(BaseModel):

&nbsp;   scan\_id: str

&nbsp;   subscription\_id: str

&nbsp;   status: ScanStatus

&nbsp;   inventoryCount: int = 0

&nbsp;   costRows: int = 0

&nbsp;   advisorRecs: int = 0

&nbsp;   policySignalsCount: int = 0

&nbsp;   networkSignalsCount: int = 0

&nbsp;   warningsCount: int = 0

&nbsp;   errorsCount: int = 0

&nbsp;   error: Optional\[str] = None

```



---



\## `services/api/app/config.py`



```python

from pydantic import BaseSettings





class Settings(BaseSettings):

&nbsp;   app\_name: str = "ACA API"

&nbsp;   cosmos\_database\_name: str = "aca"

&nbsp;   cosmos\_scans\_container: str = "scans"

&nbsp;   cosmos\_inventories\_container: str = "inventories"

&nbsp;   cosmos\_cost\_container: str = "cost-data"

&nbsp;   cosmos\_advisor\_container: str = "advisor"



&nbsp;   class Config:

&nbsp;       env\_file = ".env"





settings = Settings()

```



---



\## `services/api/app/dependencies.py`



```python

from app.repos.scans\_repo import InMemoryScansRepo

from app.services.preflight\_service import PreflightService

from app.services.scan\_service import ScanService





\_scans\_repo = InMemoryScansRepo()





def get\_scans\_repo() -> InMemoryScansRepo:

&nbsp;   return \_scans\_repo





def get\_preflight\_service() -> PreflightService:

&nbsp;   return PreflightService(scans\_repo=\_scans\_repo)





def get\_scan\_service() -> ScanService:

&nbsp;   return ScanService(scans\_repo=\_scans\_repo)

```



---



\## `services/api/app/repos/scans\_repo.py`



```python

from \_\_future\_\_ import annotations



from typing import Any, Dict, Optional





class InMemoryScansRepo:

&nbsp;   """

&nbsp;   Replace with Cosmos implementation.

&nbsp;   Partition key in real impl: subscriptionId

&nbsp;   """



&nbsp;   def \_\_init\_\_(self) -> None:

&nbsp;       self.\_docs: Dict\[str, Dict\[str, Any]] = {}



&nbsp;   async def upsert\_scan(self, doc: Dict\[str, Any]) -> Dict\[str, Any]:

&nbsp;       self.\_docs\[doc\["scan\_id"]] = doc

&nbsp;       return doc



&nbsp;   async def get\_scan(self, scan\_id: str) -> Optional\[Dict\[str, Any]]:

&nbsp;       return self.\_docs.get(scan\_id)



&nbsp;   async def update\_scan(self, scan\_id: str, \*\*fields: Any) -> Optional\[Dict\[str, Any]]:

&nbsp;       doc = self.\_docs.get(scan\_id)

&nbsp;       if not doc:

&nbsp;           return None

&nbsp;       doc.update(fields)

&nbsp;       self.\_docs\[scan\_id] = doc

&nbsp;       return doc

```



---



\## `services/api/app/services/preflight\_service.py`



```python

from \_\_future\_\_ import annotations



import uuid

from typing import List



from app.models.preflight import (

&nbsp;   ExtractionDepthResult,

&nbsp;   PreflightRequest,

&nbsp;   PreflightResponse,

&nbsp;   ProbeResult,

)





class PreflightService:

&nbsp;   def \_\_init\_\_(self, scans\_repo) -> None:

&nbsp;       self.scans\_repo = scans\_repo



&nbsp;   async def run(self, payload: dict) -> PreflightResponse:

&nbsp;       req = PreflightRequest(\*\*payload)

&nbsp;       scan\_id = f"scan\_{uuid.uuid4().hex\[:12]}"



&nbsp;       probes = await self.\_run\_probes(req)

&nbsp;       extraction\_depth = self.\_compute\_extraction\_depth(probes)

&nbsp;       top\_status = self.\_compute\_top\_status(probes)

&nbsp;       summary = self.\_build\_summary(top\_status, extraction\_depth)



&nbsp;       response = PreflightResponse(

&nbsp;           scan\_id=scan\_id,

&nbsp;           subscription\_id=req.subscriptionId,

&nbsp;           tenant\_id=req.tenantId,

&nbsp;           status=top\_status,

&nbsp;           extraction\_depth=extraction\_depth,

&nbsp;           probes=probes,

&nbsp;           summary=summary,

&nbsp;       )



&nbsp;       await self.scans\_repo.upsert\_scan(

&nbsp;           {

&nbsp;               "scan\_id": response.scan\_id,

&nbsp;               "subscription\_id": response.subscription\_id,

&nbsp;               "tenant\_id": response.tenant\_id,

&nbsp;               "status": "preflight\_warn" if top\_status == "PASS\_WITH\_WARNINGS" else (

&nbsp;                   "preflight\_failed" if top\_status == "FAIL" else "queued"

&nbsp;               ),

&nbsp;               "preflight": response.model\_dump(),

&nbsp;               "inventoryCount": 0,

&nbsp;               "costRows": 0,

&nbsp;               "advisorRecs": 0,

&nbsp;               "policySignalsCount": 0,

&nbsp;               "networkSignalsCount": 0,

&nbsp;               "warningsCount": sum(1 for p in probes if p.status == "WARN"),

&nbsp;               "errorsCount": sum(1 for p in probes if p.status == "FAIL"),

&nbsp;           }

&nbsp;       )

&nbsp;       return response



&nbsp;   async def get(self, scan\_id: str) -> PreflightResponse | None:

&nbsp;       doc = await self.scans\_repo.get\_scan(scan\_id)

&nbsp;       if not doc or "preflight" not in doc:

&nbsp;           return None

&nbsp;       return PreflightResponse(\*\*doc\["preflight"])



&nbsp;   async def \_run\_probes(self, req: PreflightRequest) -> List\[ProbeResult]:

&nbsp;       # Stubbed for now. Replace with Azure SDK / REST calls.

&nbsp;       return \[

&nbsp;           ProbeResult(

&nbsp;               probe\_name="arm\_auth",

&nbsp;               status="PASS",

&nbsp;               required\_role\_or\_permission="Valid ARM token",

&nbsp;               actual\_result="ARM token acquired successfully",

&nbsp;           ),

&nbsp;           ProbeResult(

&nbsp;               probe\_name="resource\_graph",

&nbsp;               status="PASS",

&nbsp;               required\_role\_or\_permission="Reader + Resource Graph query",

&nbsp;               actual\_result="Inventory query succeeded",

&nbsp;           ),

&nbsp;           ProbeResult(

&nbsp;               probe\_name="subscription\_reader",

&nbsp;               status="PASS",

&nbsp;               required\_role\_or\_permission="Reader",

&nbsp;               actual\_result="Subscription inventory is readable",

&nbsp;           ),

&nbsp;           ProbeResult(

&nbsp;               probe\_name="cost\_management",

&nbsp;               status="PASS",

&nbsp;               required\_role\_or\_permission="Cost Management Reader",

&nbsp;               actual\_result="Cost query succeeded for 91-day window",

&nbsp;           ),

&nbsp;           ProbeResult(

&nbsp;               probe\_name="advisor",

&nbsp;               status="PASS",

&nbsp;               required\_role\_or\_permission="Advisor read",

&nbsp;               actual\_result="Advisor recommendations accessible",

&nbsp;           ),

&nbsp;           ProbeResult(

&nbsp;               probe\_name="policy",

&nbsp;               status="WARN",

&nbsp;               required\_role\_or\_permission="Policy Insights Reader",

&nbsp;               actual\_result="Policy Insights unavailable",

&nbsp;               human\_guidance="Policy-based findings will be skipped",

&nbsp;               can\_continue\_without\_this=True,

&nbsp;               collection\_impact="Reduced governance finding coverage",

&nbsp;           ),

&nbsp;       ]



&nbsp;   def \_compute\_extraction\_depth(self, probes: List\[ProbeResult]) -> ExtractionDepthResult:

&nbsp;       probe\_map = {p.probe\_name: p.status for p in probes}



&nbsp;       if probe\_map.get("resource\_graph") != "PASS":

&nbsp;           return ExtractionDepthResult(

&nbsp;               level="DEPTH\_0\_NONE",

&nbsp;               rationale="Inventory access unavailable.",

&nbsp;           )



&nbsp;       if probe\_map.get("cost\_management") != "PASS":

&nbsp;           return ExtractionDepthResult(

&nbsp;               level="DEPTH\_1\_INVENTORY\_ONLY",

&nbsp;               rationale="Inventory available, cost data unavailable.",

&nbsp;           )



&nbsp;       if probe\_map.get("advisor") != "PASS":

&nbsp;           return ExtractionDepthResult(

&nbsp;               level="DEPTH\_2\_INVENTORY\_COST",

&nbsp;               rationale="Inventory and cost available, Advisor unavailable.",

&nbsp;           )



&nbsp;       if probe\_map.get("policy") == "PASS":

&nbsp;           return ExtractionDepthResult(

&nbsp;               level="DEPTH\_4\_ENHANCED",

&nbsp;               rationale="Inventory, cost, Advisor, and policy signals available.",

&nbsp;           )



&nbsp;       return ExtractionDepthResult(

&nbsp;           level="DEPTH\_3\_STANDARD",

&nbsp;           rationale="Inventory, cost, and Advisor available.",

&nbsp;       )



&nbsp;   def \_compute\_top\_status(self, probes: List\[ProbeResult]) -> str:

&nbsp;       if any(p.status == "FAIL" and not p.can\_continue\_without\_this for p in probes):

&nbsp;           return "FAIL"

&nbsp;       if any(p.status == "WARN" for p in probes):

&nbsp;           return "PASS\_WITH\_WARNINGS"

&nbsp;       return "PASS"



&nbsp;   def \_build\_summary(self, top\_status: str, extraction\_depth: ExtractionDepthResult) -> str:

&nbsp;       return f"Pre-flight result: {top\_status}. Extraction depth: {extraction\_depth.level}."

```



---



\## `services/api/app/services/scan\_service.py`



```python

from \_\_future\_\_ import annotations



from app.models.scans import ScanStatusResponse, StartCollectionRequest





class ScanService:

&nbsp;   def \_\_init\_\_(self, scans\_repo) -> None:

&nbsp;       self.scans\_repo = scans\_repo



&nbsp;   async def start\_collection(self, payload: dict) -> dict:

&nbsp;       req = StartCollectionRequest(\*\*payload)

&nbsp;       doc = await self.scans\_repo.get\_scan(req.scanId)

&nbsp;       if not doc:

&nbsp;           raise ValueError("Scan not found")



&nbsp;       preflight = doc.get("preflight", {})

&nbsp;       if preflight.get("status") == "FAIL":

&nbsp;           raise ValueError("Pre-flight failed; collection cannot start")



&nbsp;       await self.scans\_repo.update\_scan(req.scanId, status="running")

&nbsp;       # TODO: trigger Azure Container Apps Job here

&nbsp;       return {"scanId": req.scanId, "status": "running"}



&nbsp;   async def get\_status(self, scan\_id: str) -> ScanStatusResponse | None:

&nbsp;       doc = await self.scans\_repo.get\_scan(scan\_id)

&nbsp;       if not doc:

&nbsp;           return None

&nbsp;       return ScanStatusResponse(

&nbsp;           scan\_id=doc\["scan\_id"],

&nbsp;           subscription\_id=doc\["subscription\_id"],

&nbsp;           status=doc\["status"],

&nbsp;           inventoryCount=doc.get("inventoryCount", 0),

&nbsp;           costRows=doc.get("costRows", 0),

&nbsp;           advisorRecs=doc.get("advisorRecs", 0),

&nbsp;           policySignalsCount=doc.get("policySignalsCount", 0),

&nbsp;           networkSignalsCount=doc.get("networkSignalsCount", 0),

&nbsp;           warningsCount=doc.get("warningsCount", 0),

&nbsp;           errorsCount=doc.get("errorsCount", 0),

&nbsp;           error=doc.get("error"),

&nbsp;       )

```



---



\## `services/api/app/routes/preflight.py`



```python

from fastapi import APIRouter, Depends, HTTPException



from app.dependencies import get\_preflight\_service

from app.models.preflight import PreflightResponse

from app.services.preflight\_service import PreflightService



router = APIRouter(prefix="/v1/auth", tags=\["auth"])





@router.post("/preflight", response\_model=PreflightResponse)

async def run\_preflight(

&nbsp;   payload: dict,

&nbsp;   svc: PreflightService = Depends(get\_preflight\_service),

) -> PreflightResponse:

&nbsp;   return await svc.run(payload)





@router.get("/preflight/{scan\_id}", response\_model=PreflightResponse)

async def get\_preflight(

&nbsp;   scan\_id: str,

&nbsp;   svc: PreflightService = Depends(get\_preflight\_service),

) -> PreflightResponse:

&nbsp;   result = await svc.get(scan\_id)

&nbsp;   if not result:

&nbsp;       raise HTTPException(status\_code=404, detail="Preflight result not found")

&nbsp;   return result

```



---



\## `services/api/app/routes/collect.py`



```python

from fastapi import APIRouter, Depends, HTTPException



from app.dependencies import get\_scan\_service

from app.services.scan\_service import ScanService



router = APIRouter(prefix="/v1/collect", tags=\["collect"])





@router.post("/start")

async def start\_collection(

&nbsp;   payload: dict,

&nbsp;   svc: ScanService = Depends(get\_scan\_service),

):

&nbsp;   try:

&nbsp;       return await svc.start\_collection(payload)

&nbsp;   except ValueError as exc:

&nbsp;       raise HTTPException(status\_code=400, detail=str(exc)) from exc





@router.get("/status/{scan\_id}")

async def get\_collection\_status(

&nbsp;   scan\_id: str,

&nbsp;   svc: ScanService = Depends(get\_scan\_service),

):

&nbsp;   result = await svc.get\_status(scan\_id)

&nbsp;   if not result:

&nbsp;       raise HTTPException(status\_code=404, detail="Scan not found")

&nbsp;   return result

```



---



\## `services/api/app/routes/health.py`



```python

from fastapi import APIRouter



router = APIRouter(tags=\["health"])





@router.get("/health")

async def health() -> dict:

&nbsp;   return {"status": "ok"}

```



---



\## `services/api/app/main.py`



```python

from fastapi import FastAPI



from app.routes.collect import router as collect\_router

from app.routes.health import router as health\_router

from app.routes.preflight import router as preflight\_router



app = FastAPI(title="ACA API")



app.include\_router(health\_router)

app.include\_router(preflight\_router)

app.include\_router(collect\_router)

```



---



\## `services/collector/app/job\_context.py`



```python

from \_\_future\_\_ import annotations



from typing import Literal, Optional



from pydantic import BaseModel





class JobContext(BaseModel):

&nbsp;   scan\_id: str

&nbsp;   subscription\_id: str

&nbsp;   tenant\_id: Optional\[str] = None

&nbsp;   auth\_mode: Literal\["delegated", "service\_principal", "lighthouse"]

&nbsp;   extraction\_depth: str

&nbsp;   actor\_id: str = "collector-job"

```



---



\## `services/collector/app/utils/retry.py`



```python

from \_\_future\_\_ import annotations



import asyncio

from typing import Awaitable, Callable, TypeVar





T = TypeVar("T")





async def retry\_async(

&nbsp;   fn: Callable\[\[], Awaitable\[T]],

&nbsp;   retries: int = 5,

&nbsp;   base\_delay: float = 1.0,

) -> T:

&nbsp;   last\_exc = None

&nbsp;   for attempt in range(retries):

&nbsp;       try:

&nbsp;           return await fn()

&nbsp;       except Exception as exc:  # replace with Azure-specific retryable exceptions

&nbsp;           last\_exc = exc

&nbsp;           if attempt == retries - 1:

&nbsp;               raise

&nbsp;           await asyncio.sleep(base\_delay \* (2 \*\* attempt))

&nbsp;   raise last\_exc  # pragma: no cover

```



---



\## `services/collector/app/writers/cosmos\_writer.py`



```python

from \_\_future\_\_ import annotations





class CosmosWriter:

&nbsp;   """

&nbsp;   Replace with azure-cosmos implementation.

&nbsp;   """



&nbsp;   async def bulk\_upsert(self, container\_name: str, partition\_key: str, docs: list\[dict]) -> int:

&nbsp;       # TODO: real Cosmos bulk upsert

&nbsp;       return len(docs)

```



---



\## `services/collector/app/collectors/inventory.py`



```python

from \_\_future\_\_ import annotations



from services.collector.app.utils.retry import retry\_async





class InventoryCollector:

&nbsp;   def \_\_init\_\_(self, writer) -> None:

&nbsp;       self.writer = writer



&nbsp;   async def collect(self, ctx) -> list\[dict]:

&nbsp;       async def \_query() -> list\[dict]:

&nbsp;           # TODO: Azure Resource Graph query

&nbsp;           return \[

&nbsp;               {

&nbsp;                   "subscriptionId": ctx.subscription\_id,

&nbsp;                   "resourceId": "/subscriptions/xxx/resourceGroups/rg/providers/Microsoft.Compute/virtualMachines/vm1",

&nbsp;                   "type": "Microsoft.Compute/virtualMachines",

&nbsp;                   "name": "vm1",

&nbsp;                   "resourceGroup": "rg",

&nbsp;                   "location": "canadacentral",

&nbsp;                   "sku": "Standard\_D4s\_v5",

&nbsp;                   "tags": {"env": "dev"},

&nbsp;               }

&nbsp;           ]



&nbsp;       docs = await retry\_async(\_query)

&nbsp;       await self.writer.bulk\_upsert("inventories", ctx.subscription\_id, docs)

&nbsp;       return docs

```



---



\## `services/collector/app/collectors/cost.py`



```python

from \_\_future\_\_ import annotations



from services.collector.app.utils.retry import retry\_async





class CostCollector:

&nbsp;   def \_\_init\_\_(self, writer) -> None:

&nbsp;       self.writer = writer



&nbsp;   async def collect(self, ctx) -> list\[dict]:

&nbsp;       async def \_query() -> list\[dict]:

&nbsp;           # TODO: Cost Management Query API with 91-day daily rows + paging

&nbsp;           return \[

&nbsp;               {

&nbsp;                   "subscriptionId": ctx.subscription\_id,

&nbsp;                   "date": "2026-03-01",

&nbsp;                   "MeterCategory": "Virtual Machines",

&nbsp;                   "MeterName": "D4s v5",

&nbsp;                   "resourceGroup": "rg",

&nbsp;                   "resourceId": "hashed\_or\_raw\_resource\_id",

&nbsp;                   "PreTaxCost": 42.13,

&nbsp;                   "currency": "CAD",

&nbsp;               }

&nbsp;           ]



&nbsp;       docs = await retry\_async(\_query)

&nbsp;       await self.writer.bulk\_upsert("cost-data", ctx.subscription\_id, docs)

&nbsp;       return docs

```



---



\## `services/collector/app/collectors/advisor.py`



```python

from \_\_future\_\_ import annotations



from services.collector.app.utils.retry import retry\_async





class AdvisorCollector:

&nbsp;   def \_\_init\_\_(self, writer) -> None:

&nbsp;       self.writer = writer



&nbsp;   async def collect(self, ctx) -> list\[dict]:

&nbsp;       async def \_query() -> list\[dict]:

&nbsp;           # TODO: Azure Advisor API

&nbsp;           return \[

&nbsp;               {

&nbsp;                   "subscriptionId": ctx.subscription\_id,

&nbsp;                   "recommendationId": "rec-001",

&nbsp;                   "category": "Cost",

&nbsp;                   "impact": "High",

&nbsp;                   "shortDescription": "Resize underutilized VM",

&nbsp;                   "resourceId": "/subscriptions/xxx/resourceGroups/rg/providers/Microsoft.Compute/virtualMachines/vm1",

&nbsp;                   "raw": {"sample": True},

&nbsp;               }

&nbsp;           ]



&nbsp;       docs = await retry\_async(\_query)

&nbsp;       await self.writer.bulk\_upsert("advisor", ctx.subscription\_id, docs)

&nbsp;       return docs

```



---



\## `services/collector/app/collectors/policy.py`



```python

class PolicyCollector:

&nbsp;   async def collect(self, ctx) -> dict:

&nbsp;       # TODO: Azure Policy Insights

&nbsp;       return {"policySignalsCount": 0}

```



---



\## `services/collector/app/collectors/network.py`



```python

class NetworkCollector:

&nbsp;   async def collect(self, ctx) -> dict:

&nbsp;       # TODO: ARM topology reads

&nbsp;       return {"networkSignalsCount": 0}

```



---



\## `services/collector/app/collectors/activity.py`



```python

class ActivityCollector:

&nbsp;   async def collect(self, ctx) -> dict:

&nbsp;       # TODO: Activity / Log Analytics optional usage signals

&nbsp;       return {"activitySignalsCount": 0}

```



---



\## `services/collector/app/orchestrator.py`



```python

from \_\_future\_\_ import annotations



from services.collector.app.collectors.activity import ActivityCollector

from services.collector.app.collectors.advisor import AdvisorCollector

from services.collector.app.collectors.cost import CostCollector

from services.collector.app.collectors.inventory import InventoryCollector

from services.collector.app.collectors.network import NetworkCollector

from services.collector.app.collectors.policy import PolicyCollector

from services.collector.app.writers.cosmos\_writer import CosmosWriter





class CollectorOrchestrator:

&nbsp;   def \_\_init\_\_(self, scans\_repo) -> None:

&nbsp;       self.scans\_repo = scans\_repo

&nbsp;       writer = CosmosWriter()

&nbsp;       self.inventory = InventoryCollector(writer)

&nbsp;       self.cost = CostCollector(writer)

&nbsp;       self.advisor = AdvisorCollector(writer)

&nbsp;       self.policy = PolicyCollector()

&nbsp;       self.network = NetworkCollector()

&nbsp;       self.activity = ActivityCollector()



&nbsp;   async def run(self, ctx) -> None:

&nbsp;       await self.scans\_repo.update\_scan(ctx.scan\_id, status="running")



&nbsp;       stats = {

&nbsp;           "inventoryCount": 0,

&nbsp;           "costRows": 0,

&nbsp;           "advisorRecs": 0,

&nbsp;           "policySignalsCount": 0,

&nbsp;           "networkSignalsCount": 0,

&nbsp;           "warningsCount": 0,

&nbsp;           "errorsCount": 0,

&nbsp;       }



&nbsp;       try:

&nbsp;           inventory\_docs = await self.inventory.collect(ctx)

&nbsp;           stats\["inventoryCount"] = len(inventory\_docs)



&nbsp;           if ctx.extraction\_depth in {

&nbsp;               "DEPTH\_2\_INVENTORY\_COST",

&nbsp;               "DEPTH\_3\_STANDARD",

&nbsp;               "DEPTH\_4\_ENHANCED",

&nbsp;               "DEPTH\_5\_ACTIVITY\_ENHANCED",

&nbsp;           }:

&nbsp;               cost\_docs = await self.cost.collect(ctx)

&nbsp;               stats\["costRows"] = len(cost\_docs)



&nbsp;           if ctx.extraction\_depth in {

&nbsp;               "DEPTH\_3\_STANDARD",

&nbsp;               "DEPTH\_4\_ENHANCED",

&nbsp;               "DEPTH\_5\_ACTIVITY\_ENHANCED",

&nbsp;           }:

&nbsp;               advisor\_docs = await self.advisor.collect(ctx)

&nbsp;               stats\["advisorRecs"] = len(advisor\_docs)



&nbsp;           if ctx.extraction\_depth in {"DEPTH\_4\_ENHANCED", "DEPTH\_5\_ACTIVITY\_ENHANCED"}:

&nbsp;               policy\_stats = await self.policy.collect(ctx)

&nbsp;               network\_stats = await self.network.collect(ctx)

&nbsp;               stats.update(policy\_stats)

&nbsp;               stats.update(network\_stats)



&nbsp;           if ctx.extraction\_depth == "DEPTH\_5\_ACTIVITY\_ENHANCED":

&nbsp;               await self.activity.collect(ctx)



&nbsp;           await self.scans\_repo.update\_scan(ctx.scan\_id, status="succeeded", \*\*stats)



&nbsp;       except Exception as exc:

&nbsp;           stats\["errorsCount"] += 1

&nbsp;           await self.scans\_repo.update\_scan(

&nbsp;               ctx.scan\_id,

&nbsp;               status="failed",

&nbsp;               error=str(exc),

&nbsp;               \*\*stats,

&nbsp;           )

&nbsp;           raise

```



---



\## `tests/unit/test\_preflight\_service.py`



```python

import pytest



from app.repos.scans\_repo import InMemoryScansRepo

from app.services.preflight\_service import PreflightService





@pytest.mark.asyncio

async def test\_preflight\_returns\_standard\_or\_enhanced\_depth():

&nbsp;   repo = InMemoryScansRepo()

&nbsp;   svc = PreflightService(scans\_repo=repo)



&nbsp;   result = await svc.run({"subscriptionId": "sub-123", "mode": "delegated"})



&nbsp;   assert result.subscription\_id == "sub-123"

&nbsp;   assert result.status in {"PASS", "PASS\_WITH\_WARNINGS"}

&nbsp;   assert result.extraction\_depth.level in {"DEPTH\_3\_STANDARD", "DEPTH\_4\_ENHANCED"}

```



---



\## `tests/integration/test\_preflight\_api.py`



```python

from fastapi.testclient import TestClient



from app.main import app





def test\_preflight\_api():

&nbsp;   client = TestClient(app)

&nbsp;   response = client.post(

&nbsp;       "/v1/auth/preflight",

&nbsp;       json={"subscriptionId": "sub-123", "mode": "delegated"},

&nbsp;   )

&nbsp;   assert response.status\_code == 200

&nbsp;   body = response.json()

&nbsp;   assert body\["subscription\_id"] == "sub-123"

&nbsp;   assert "probes" in body

```



---



\## Next build steps



1\. Replace the stubbed probes with real Azure SDK / REST calls.

2\. Swap `InMemoryScansRepo` for a Cosmos implementation.

3\. Add Container Apps Job trigger logic in `ScanService`.

4\. Add paging and throttling support in `CostCollector`.

5\. Add real normalization contracts for inventory, cost, and Advisor.

6\. Add policy, network, and activity collectors progressively.



If you want, the next step should be the \*\*real Cosmos repo implementation + Azure SDK probe stubs\*\*.




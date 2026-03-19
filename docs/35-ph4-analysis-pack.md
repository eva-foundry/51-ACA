Excellent. Here is \*\*Phase 4: ACA analysis engine starter pack\*\*.



This is the phase where ACA stops being just a collector and starts becoming the product:



\* collected data → normalized signals

\* signals → findings

\* findings → Pareto-ranked recommendations

\* recommendations → scripts / deliverables later



I’ll give you a practical starter structure that fits what you’ve already built.



---



\## Goal of this phase



Build the first analysis engine that:



\* reads normalized data from Cosmos

\* evaluates rules

\* emits structured findings

\* computes \*\*priority / Pareto score\*\*

\* stores findings for API and report generation



This phase should support your first high-value findings such as:



\* \*\*night shutdown opportunity for dev resources\*\*

\* \*\*ghost resources\*\*

\* \*\*underutilized / obvious Azure waste\*\*

\* \*\*Advisor-backed validation findings\*\*



---



\# Suggested repo additions



```text

services/

&nbsp; analysis/

&nbsp;   app/

&nbsp;     main.py

&nbsp;     orchestrator.py

&nbsp;     analysis\_context.py

&nbsp;     contracts/

&nbsp;       finding\_contract.py

&nbsp;       rule\_contract.py

&nbsp;     models/

&nbsp;       finding.py

&nbsp;       analysis\_run.py

&nbsp;     repos/

&nbsp;       findings\_repo.py

&nbsp;       scans\_read\_repo.py

&nbsp;       inventories\_read\_repo.py

&nbsp;       cost\_read\_repo.py

&nbsp;       advisor\_read\_repo.py

&nbsp;     rules/

&nbsp;       base.py

&nbsp;       ghost\_unattached\_disks.py

&nbsp;       ghost\_public\_ips.py

&nbsp;       dev\_night\_shutdown.py

&nbsp;       advisor\_cost\_high\_impact.py

&nbsp;     scoring/

&nbsp;       pareto.py

&nbsp;     utils/

&nbsp;       grouping.py

&nbsp;       time\_windows.py

&nbsp;       confidence.py

```



---



\# Core design



The analysis engine should work like this:



```text

scan collected

&nbsp;   ↓

analysis job starts

&nbsp;   ↓

rules load scan data

&nbsp;   ↓

rules emit findings

&nbsp;   ↓

Pareto scoring ranks findings

&nbsp;   ↓

findings saved to Cosmos

&nbsp;   ↓

later delivery/report step packages them

```



---



\# 1. Rule contract



\## `services/analysis/app/contracts/rule\_contract.py`



```python

from \_\_future\_\_ import annotations



from typing import Protocol



from services.analysis.app.analysis\_context import AnalysisContext

from services.analysis.app.models.finding import Finding





class AnalysisRule(Protocol):

&nbsp;   rule\_id: str

&nbsp;   rule\_name: str

&nbsp;   rule\_category: str

&nbsp;   severity\_default: str



&nbsp;   async def run(self, ctx: AnalysisContext) -> list\[Finding]:

&nbsp;       ...

```



---



\# 2. Finding model



\## `services/analysis/app/models/finding.py`



```python

from \_\_future\_\_ import annotations



from typing import Any, Literal, Optional



from pydantic import BaseModel





FindingSeverity = Literal\["low", "medium", "high", "critical"]

FindingCategory = Literal\[

&nbsp;   "ghost\_resource",

&nbsp;   "idle\_resource",

&nbsp;   "shutdown\_opportunity",

&nbsp;   "rightsizing",

&nbsp;   "advisor\_validated",

&nbsp;   "reservation\_opportunity",

&nbsp;   "governance\_signal",

]

FindingStatus = Literal\["open", "accepted", "dismissed", "resolved"]





class Finding(BaseModel):

&nbsp;   id: str

&nbsp;   subscriptionId: str

&nbsp;   scanId: str



&nbsp;   ruleId: str

&nbsp;   ruleName: str

&nbsp;   category: FindingCategory

&nbsp;   severity: FindingSeverity

&nbsp;   status: FindingStatus = "open"



&nbsp;   title: str

&nbsp;   description: str



&nbsp;   resourceId: Optional\[str] = None

&nbsp;   resourceType: Optional\[str] = None

&nbsp;   resourceName: Optional\[str] = None

&nbsp;   resourceGroup: Optional\[str] = None

&nbsp;   region: Optional\[str] = None



&nbsp;   monthlySavingsEstimate: float = 0.0

&nbsp;   annualSavingsEstimate: float = 0.0

&nbsp;   confidenceScore: float = 0.0

&nbsp;   implementationRiskScore: float = 0.0

&nbsp;   priorityScore: float = 0.0



&nbsp;   rationale: list\[str] = \[]

&nbsp;   evidence: dict\[str, Any] = {}

&nbsp;   recommendedAction: Optional\[str] = None

&nbsp;   scriptTemplateId: Optional\[str] = None



&nbsp;   tags: dict\[str, str] = {}

&nbsp;   raw: dict\[str, Any] = {}

```



---



\# 3. Analysis run model



\## `services/analysis/app/models/analysis\_run.py`



```python

from \_\_future\_\_ import annotations



from typing import Literal



from pydantic import BaseModel





AnalysisStatus = Literal\["queued", "running", "succeeded", "failed"]





class AnalysisRun(BaseModel):

&nbsp;   analysisRunId: str

&nbsp;   subscriptionId: str

&nbsp;   scanId: str

&nbsp;   status: AnalysisStatus

&nbsp;   findingsCount: int = 0

&nbsp;   warningsCount: int = 0

&nbsp;   errorsCount: int = 0

```



---



\# 4. Analysis context



\## `services/analysis/app/analysis\_context.py`



```python

from \_\_future\_\_ import annotations



from pydantic import BaseModel





class AnalysisContext(BaseModel):

&nbsp;   scan\_id: str

&nbsp;   subscription\_id: str



&nbsp;   inventory\_docs: list\[dict]

&nbsp;   cost\_docs: list\[dict]

&nbsp;   advisor\_docs: list\[dict]

&nbsp;   policy\_summary: dict | None = None

&nbsp;   network\_summary: dict | None = None

&nbsp;   activity\_summary: dict | None = None

```



---



\# 5. Findings repo



\## `services/analysis/app/repos/findings\_repo.py`



```python

from \_\_future\_\_ import annotations



from app.repos.cosmos\_base import CosmosClientFactory, CosmosContainerHelper, bulk\_upsert\_items





class FindingsRepo:

&nbsp;   CONTAINER = "findings"



&nbsp;   def \_\_init\_\_(self) -> None:

&nbsp;       self.factory = CosmosClientFactory()



&nbsp;   async def \_container(self):

&nbsp;       db = await self.factory.get\_database\_client()

&nbsp;       helper = CosmosContainerHelper(db, self.CONTAINER)

&nbsp;       return await helper.get\_container()



&nbsp;   async def create\_container\_if\_missing(self):

&nbsp;       db = await self.factory.get\_database\_client()

&nbsp;       helper = CosmosContainerHelper(db, self.CONTAINER)

&nbsp;       await helper.ensure\_container("/subscriptionId")



&nbsp;   async def bulk\_upsert(self, subscription\_id: str, docs: list\[dict]) -> int:

&nbsp;       for d in docs:

&nbsp;           d\["subscriptionId"] = subscription\_id

&nbsp;       container = await self.\_container()

&nbsp;       return await bulk\_upsert\_items(container, docs)

```



---



\# 6. Read repos



\## `services/analysis/app/repos/inventories\_read\_repo.py`



```python

from \_\_future\_\_ import annotations



from app.repos.cosmos\_base import CosmosClientFactory, CosmosContainerHelper





class InventoriesReadRepo:

&nbsp;   CONTAINER = "inventories"



&nbsp;   def \_\_init\_\_(self) -> None:

&nbsp;       self.factory = CosmosClientFactory()



&nbsp;   async def \_container(self):

&nbsp;       db = await self.factory.get\_database\_client()

&nbsp;       helper = CosmosContainerHelper(db, self.CONTAINER)

&nbsp;       return await helper.get\_container()



&nbsp;   async def by\_subscription(self, subscription\_id: str) -> list\[dict]:

&nbsp;       container = await self.\_container()

&nbsp;       items = container.query\_items(

&nbsp;           query="SELECT \* FROM c",

&nbsp;           partition\_key=subscription\_id,

&nbsp;       )

&nbsp;       results = \[]

&nbsp;       async for item in items:

&nbsp;           results.append(item)

&nbsp;       return results

```



\## `services/analysis/app/repos/cost\_read\_repo.py`



```python

from \_\_future\_\_ import annotations



from app.repos.cosmos\_base import CosmosClientFactory, CosmosContainerHelper





class CostReadRepo:

&nbsp;   CONTAINER = "cost-data"



&nbsp;   def \_\_init\_\_(self) -> None:

&nbsp;       self.factory = CosmosClientFactory()



&nbsp;   async def \_container(self):

&nbsp;       db = await self.factory.get\_database\_client()

&nbsp;       helper = CosmosContainerHelper(db, self.CONTAINER)

&nbsp;       return await helper.get\_container()



&nbsp;   async def by\_subscription(self, subscription\_id: str) -> list\[dict]:

&nbsp;       container = await self.\_container()

&nbsp;       items = container.query\_items(

&nbsp;           query="SELECT \* FROM c",

&nbsp;           partition\_key=subscription\_id,

&nbsp;       )

&nbsp;       results = \[]

&nbsp;       async for item in items:

&nbsp;           results.append(item)

&nbsp;       return results

```



\## `services/analysis/app/repos/advisor\_read\_repo.py`



```python

from \_\_future\_\_ import annotations



from app.repos.cosmos\_base import CosmosClientFactory, CosmosContainerHelper





class AdvisorReadRepo:

&nbsp;   CONTAINER = "advisor"



&nbsp;   def \_\_init\_\_(self) -> None:

&nbsp;       self.factory = CosmosClientFactory()



&nbsp;   async def \_container(self):

&nbsp;       db = await self.factory.get\_database\_client()

&nbsp;       helper = CosmosContainerHelper(db, self.CONTAINER)

&nbsp;       return await helper.get\_container()



&nbsp;   async def by\_subscription(self, subscription\_id: str) -> list\[dict]:

&nbsp;       container = await self.\_container()

&nbsp;       items = container.query\_items(

&nbsp;           query="SELECT \* FROM c",

&nbsp;           partition\_key=subscription\_id,

&nbsp;       )

&nbsp;       results = \[]

&nbsp;       async for item in items:

&nbsp;           results.append(item)

&nbsp;       return results

```



---



\# 7. Pareto scoring



\## `services/analysis/app/scoring/pareto.py`



```python

from \_\_future\_\_ import annotations



from services.analysis.app.models.finding import Finding





def compute\_priority\_score(

&nbsp;   annual\_savings: float,

&nbsp;   confidence: float,

&nbsp;   implementation\_risk: float,

) -> float:

&nbsp;   """

&nbsp;   Simple first version:

&nbsp;   score = savings \* confidence / max(risk, 0.1)

&nbsp;   Lower risk -> higher priority.

&nbsp;   """

&nbsp;   risk = max(implementation\_risk, 0.1)

&nbsp;   return round((annual\_savings \* confidence) / risk, 2)





def rank\_findings(findings: list\[Finding]) -> list\[Finding]:

&nbsp;   for f in findings:

&nbsp;       f.priorityScore = compute\_priority\_score(

&nbsp;           annual\_savings=f.annualSavingsEstimate,

&nbsp;           confidence=f.confidenceScore,

&nbsp;           implementation\_risk=f.implementationRiskScore,

&nbsp;       )

&nbsp;   return sorted(findings, key=lambda x: x.priorityScore, reverse=True)

```



---



\# 8. Base rule helper



\## `services/analysis/app/rules/base.py`



```python

from \_\_future\_\_ import annotations



import uuid





def make\_finding\_id(rule\_id: str, resource\_id: str | None) -> str:

&nbsp;   suffix = uuid.uuid5(uuid.NAMESPACE\_URL, f"{rule\_id}:{resource\_id or 'global'}").hex\[:16]

&nbsp;   return f"{rule\_id}:{suffix}"

```



---



\# 9. Ghost unattached disks rule



\## `services/analysis/app/rules/ghost\_unattached\_disks.py`



```python

from \_\_future\_\_ import annotations



from services.analysis.app.analysis\_context import AnalysisContext

from services.analysis.app.models.finding import Finding

from services.analysis.app.rules.base import make\_finding\_id





class GhostUnattachedDisksRule:

&nbsp;   rule\_id = "ghost\_unattached\_disks"

&nbsp;   rule\_name = "Ghost Unattached Disks"

&nbsp;   rule\_category = "ghost\_resource"

&nbsp;   severity\_default = "high"



&nbsp;   async def run(self, ctx: AnalysisContext) -> list\[Finding]:

&nbsp;       findings: list\[Finding] = \[]



&nbsp;       disks = \[

&nbsp;           r for r in ctx.inventory\_docs

&nbsp;           if (r.get("type") or "").lower() == "microsoft.compute/disks"

&nbsp;       ]



&nbsp;       for disk in disks:

&nbsp;           raw = disk.get("raw", {})

&nbsp;           managed\_by = raw.get("managedBy")

&nbsp;           sku = (disk.get("sku") or {}).get("name") if isinstance(disk.get("sku"), dict) else disk.get("sku")



&nbsp;           if managed\_by:

&nbsp;               continue



&nbsp;           monthly\_estimate = 25.0

&nbsp;           if sku and "premium" in str(sku).lower():

&nbsp;               monthly\_estimate = 60.0



&nbsp;           annual\_estimate = monthly\_estimate \* 12



&nbsp;           findings.append(

&nbsp;               Finding(

&nbsp;                   id=make\_finding\_id(self.rule\_id, disk.get("resourceId")),

&nbsp;                   subscriptionId=ctx.subscription\_id,

&nbsp;                   scanId=ctx.scan\_id,

&nbsp;                   ruleId=self.rule\_id,

&nbsp;                   ruleName=self.rule\_name,

&nbsp;                   category="ghost\_resource",

&nbsp;                   severity="high",

&nbsp;                   title=f"Candidate ghost disk: {disk.get('name')}",

&nbsp;                   description="Managed disk appears unattached and may no longer provide operational value.",

&nbsp;                   resourceId=disk.get("resourceId"),

&nbsp;                   resourceType=disk.get("type"),

&nbsp;                   resourceName=disk.get("name"),

&nbsp;                   resourceGroup=disk.get("resourceGroup"),

&nbsp;                   region=disk.get("location"),

&nbsp;                   monthlySavingsEstimate=monthly\_estimate,

&nbsp;                   annualSavingsEstimate=annual\_estimate,

&nbsp;                   confidenceScore=0.92,

&nbsp;                   implementationRiskScore=0.25,

&nbsp;                   rationale=\[

&nbsp;                       "Disk appears unattached (managedBy missing).",

&nbsp;                       "Unattached managed disks often continue generating storage cost.",

&nbsp;                       "Validate owner and retention requirement before deletion.",

&nbsp;                   ],

&nbsp;                   evidence={

&nbsp;                       "managedBy": managed\_by,

&nbsp;                       "sku": sku,

&nbsp;                   },

&nbsp;                   recommendedAction="Validate ownership; archive or delete if confirmed unused.",

&nbsp;                   scriptTemplateId="delete\_unattached\_disk",

&nbsp;                   raw={"resource": disk},

&nbsp;               )

&nbsp;           )



&nbsp;       return findings

```



---



\# 10. Ghost public IPs rule



\## `services/analysis/app/rules/ghost\_public\_ips.py`



```python

from \_\_future\_\_ import annotations



from services.analysis.app.analysis\_context import AnalysisContext

from services.analysis.app.models.finding import Finding

from services.analysis.app.rules.base import make\_finding\_id





class GhostPublicIPsRule:

&nbsp;   rule\_id = "ghost\_public\_ips"

&nbsp;   rule\_name = "Ghost Public IPs"

&nbsp;   rule\_category = "ghost\_resource"

&nbsp;   severity\_default = "medium"



&nbsp;   async def run(self, ctx: AnalysisContext) -> list\[Finding]:

&nbsp;       findings: list\[Finding] = \[]



&nbsp;       pips = \[

&nbsp;           r for r in ctx.inventory\_docs

&nbsp;           if (r.get("type") or "").lower() == "microsoft.network/publicipaddresses"

&nbsp;       ]



&nbsp;       for pip in pips:

&nbsp;           raw = pip.get("raw", {})

&nbsp;           ip\_config = raw.get("properties", {}).get("ipConfiguration")

&nbsp;           if ip\_config:

&nbsp;               continue



&nbsp;           monthly\_estimate = 5.0

&nbsp;           annual\_estimate = monthly\_estimate \* 12



&nbsp;           findings.append(

&nbsp;               Finding(

&nbsp;                   id=make\_finding\_id(self.rule\_id, pip.get("resourceId")),

&nbsp;                   subscriptionId=ctx.subscription\_id,

&nbsp;                   scanId=ctx.scan\_id,

&nbsp;                   ruleId=self.rule\_id,

&nbsp;                   ruleName=self.rule\_name,

&nbsp;                   category="ghost\_resource",

&nbsp;                   severity="medium",

&nbsp;                   title=f"Candidate ghost public IP: {pip.get('name')}",

&nbsp;                   description="Public IP appears unattached and may no longer be required.",

&nbsp;                   resourceId=pip.get("resourceId"),

&nbsp;                   resourceType=pip.get("type"),

&nbsp;                   resourceName=pip.get("name"),

&nbsp;                   resourceGroup=pip.get("resourceGroup"),

&nbsp;                   region=pip.get("location"),

&nbsp;                   monthlySavingsEstimate=monthly\_estimate,

&nbsp;                   annualSavingsEstimate=annual\_estimate,

&nbsp;                   confidenceScore=0.90,

&nbsp;                   implementationRiskScore=0.20,

&nbsp;                   rationale=\[

&nbsp;                       "Public IP appears unattached (no ipConfiguration).",

&nbsp;                       "Unattached public IPs can continue generating cost.",

&nbsp;                   ],

&nbsp;                   evidence={"ipConfiguration": ip\_config},

&nbsp;                   recommendedAction="Validate owner and delete if no active workload depends on it.",

&nbsp;                   scriptTemplateId="delete\_public\_ip",

&nbsp;                   raw={"resource": pip},

&nbsp;               )

&nbsp;           )



&nbsp;       return findings

```



---



\# 11. Dev night shutdown rule



\## `services/analysis/app/rules/dev\_night\_shutdown.py`



```python

from \_\_future\_\_ import annotations



from collections import defaultdict



from services.analysis.app.analysis\_context import AnalysisContext

from services.analysis.app.models.finding import Finding

from services.analysis.app.rules.base import make\_finding\_id





class DevNightShutdownRule:

&nbsp;   rule\_id = "dev\_night\_shutdown"

&nbsp;   rule\_name = "Night Shutdown Opportunity"

&nbsp;   rule\_category = "shutdown\_opportunity"

&nbsp;   severity\_default = "high"



&nbsp;   async def run(self, ctx: AnalysisContext) -> list\[Finding]:

&nbsp;       findings: list\[Finding] = \[]



&nbsp;       vm\_resources = {

&nbsp;           r.get("resourceId"): r

&nbsp;           for r in ctx.inventory\_docs

&nbsp;           if (r.get("type") or "").lower() == "microsoft.compute/virtualmachines"

&nbsp;       }



&nbsp;       cost\_by\_resource = defaultdict(float)

&nbsp;       for row in ctx.cost\_docs:

&nbsp;           rid = row.get("resourceId")

&nbsp;           if rid:

&nbsp;               cost\_by\_resource\[rid] += float(row.get("PreTaxCost") or 0.0)



&nbsp;       for resource\_id, vm in vm\_resources.items():

&nbsp;           tags = vm.get("tags") or {}

&nbsp;           name = (vm.get("name") or "").lower()

&nbsp;           env\_tag = (tags.get("env") or tags.get("environment") or "").lower()



&nbsp;           looks\_like\_dev = (

&nbsp;               env\_tag in {"dev", "development", "test", "qa", "sandbox"}

&nbsp;               or "dev" in name

&nbsp;               or "test" in name

&nbsp;               or "sandbox" in name

&nbsp;           )



&nbsp;           if not looks\_like\_dev:

&nbsp;               continue



&nbsp;           current\_91d\_cost = cost\_by\_resource.get(resource\_id, 0.0)

&nbsp;           if current\_91d\_cost <= 0:

&nbsp;               continue



&nbsp;           monthly\_estimate = current\_91d\_cost / 3.0

&nbsp;           annual\_estimate = monthly\_estimate \* 12 \* 0.33



&nbsp;           findings.append(

&nbsp;               Finding(

&nbsp;                   id=make\_finding\_id(self.rule\_id, resource\_id),

&nbsp;                   subscriptionId=ctx.subscription\_id,

&nbsp;                   scanId=ctx.scan\_id,

&nbsp;                   ruleId=self.rule\_id,

&nbsp;                   ruleName=self.rule\_name,

&nbsp;                   category="shutdown\_opportunity",

&nbsp;                   severity="high",

&nbsp;                   title=f"Night shutdown opportunity for {vm.get('name')}",

&nbsp;                   description="Development-pattern VM appears suitable for scheduled shutdown outside working hours.",

&nbsp;                   resourceId=resource\_id,

&nbsp;                   resourceType=vm.get("type"),

&nbsp;                   resourceName=vm.get("name"),

&nbsp;                   resourceGroup=vm.get("resourceGroup"),

&nbsp;                   region=vm.get("location"),

&nbsp;                   monthlySavingsEstimate=round(monthly\_estimate \* 0.33, 2),

&nbsp;                   annualSavingsEstimate=round(annual\_estimate, 2),

&nbsp;                   confidenceScore=0.82,

&nbsp;                   implementationRiskScore=0.35,

&nbsp;                   rationale=\[

&nbsp;                       "Resource naming/tagging suggests non-production usage.",

&nbsp;                       "VM cost pattern indicates recurring compute spend.",

&nbsp;                       "Scheduled shutdown for dev workloads often reduces cost by ~25–40%.",

&nbsp;                   ],

&nbsp;                   evidence={

&nbsp;                       "tags": tags,

&nbsp;                       "last91dCost": round(current\_91d\_cost, 2),

&nbsp;                   },

&nbsp;                   recommendedAction="Implement weekday schedule for startup/shutdown and validate developer usage patterns.",

&nbsp;                   scriptTemplateId="vm\_schedule\_shutdown",

&nbsp;                   raw={"resource": vm},

&nbsp;               )

&nbsp;           )



&nbsp;       return findings

```



---



\# 12. Advisor cost high impact rule



\## `services/analysis/app/rules/advisor\_cost\_high\_impact.py`



```python

from \_\_future\_\_ import annotations



from services.analysis.app.analysis\_context import AnalysisContext

from services.analysis.app.models.finding import Finding

from services.analysis.app.rules.base import make\_finding\_id





class AdvisorCostHighImpactRule:

&nbsp;   rule\_id = "advisor\_cost\_high\_impact"

&nbsp;   rule\_name = "Advisor Cost High Impact"

&nbsp;   rule\_category = "advisor\_validated"

&nbsp;   severity\_default = "medium"



&nbsp;   async def run(self, ctx: AnalysisContext) -> list\[Finding]:

&nbsp;       findings: list\[Finding] = \[]



&nbsp;       for rec in ctx.advisor\_docs:

&nbsp;           category = (rec.get("category") or "").lower()

&nbsp;           impact = (rec.get("impact") or "").lower()



&nbsp;           if category != "cost":

&nbsp;               continue

&nbsp;           if impact not in {"high", "medium"}:

&nbsp;               continue



&nbsp;           annual\_savings = float(rec.get("annualSavingsAmount") or 0.0)

&nbsp;           if annual\_savings <= 0:

&nbsp;               annual\_savings = 1200.0



&nbsp;           findings.append(

&nbsp;               Finding(

&nbsp;                   id=make\_finding\_id(self.rule\_id, rec.get("resourceId")),

&nbsp;                   subscriptionId=ctx.subscription\_id,

&nbsp;                   scanId=ctx.scan\_id,

&nbsp;                   ruleId=self.rule\_id,

&nbsp;                   ruleName=self.rule\_name,

&nbsp;                   category="advisor\_validated",

&nbsp;                   severity="medium" if impact == "medium" else "high",

&nbsp;                   title=f"Advisor cost recommendation for {rec.get('resourceId') or 'resource'}",

&nbsp;                   description=rec.get("problem") or "Azure Advisor produced a cost optimization recommendation.",

&nbsp;                   resourceId=rec.get("resourceId"),

&nbsp;                   monthlySavingsEstimate=round(annual\_savings / 12.0, 2),

&nbsp;                   annualSavingsEstimate=round(annual\_savings, 2),

&nbsp;                   confidenceScore=0.88,

&nbsp;                   implementationRiskScore=0.45,

&nbsp;                   rationale=\[

&nbsp;                       "Azure Advisor flagged this resource for cost optimization.",

&nbsp;                       f"Impact level reported by Advisor: {rec.get('impact')}.",

&nbsp;                   ],

&nbsp;                   evidence={"advisor": rec},

&nbsp;                   recommendedAction=rec.get("solution") or "Review Azure Advisor recommendation and validate implementation.",

&nbsp;                   scriptTemplateId="advisor\_followup",

&nbsp;                   raw={"advisor": rec},

&nbsp;               )

&nbsp;           )



&nbsp;       return findings

```



---



\# 13. Analysis orchestrator



\## `services/analysis/app/orchestrator.py`



```python

from \_\_future\_\_ import annotations



from services.analysis.app.analysis\_context import AnalysisContext

from services.analysis.app.repos.advisor\_read\_repo import AdvisorReadRepo

from services.analysis.app.repos.cost\_read\_repo import CostReadRepo

from services.analysis.app.repos.findings\_repo import FindingsRepo

from services.analysis.app.repos.inventories\_read\_repo import InventoriesReadRepo

from services.analysis.app.rules.advisor\_cost\_high\_impact import AdvisorCostHighImpactRule

from services.analysis.app.rules.dev\_night\_shutdown import DevNightShutdownRule

from services.analysis.app.rules.ghost\_public\_ips import GhostPublicIPsRule

from services.analysis.app.rules.ghost\_unattached\_disks import GhostUnattachedDisksRule

from services.analysis.app.scoring.pareto import rank\_findings





class AnalysisOrchestrator:

&nbsp;   def \_\_init\_\_(self) -> None:

&nbsp;       self.inventory\_repo = InventoriesReadRepo()

&nbsp;       self.cost\_repo = CostReadRepo()

&nbsp;       self.advisor\_repo = AdvisorReadRepo()

&nbsp;       self.findings\_repo = FindingsRepo()



&nbsp;       self.rules = \[

&nbsp;           GhostUnattachedDisksRule(),

&nbsp;           GhostPublicIPsRule(),

&nbsp;           DevNightShutdownRule(),

&nbsp;           AdvisorCostHighImpactRule(),

&nbsp;       ]



&nbsp;   async def run(self, subscription\_id: str, scan\_id: str) -> dict:

&nbsp;       inventory\_docs = await self.inventory\_repo.by\_subscription(subscription\_id)

&nbsp;       cost\_docs = await self.cost\_repo.by\_subscription(subscription\_id)

&nbsp;       advisor\_docs = await self.advisor\_repo.by\_subscription(subscription\_id)



&nbsp;       ctx = AnalysisContext(

&nbsp;           subscription\_id=subscription\_id,

&nbsp;           scan\_id=scan\_id,

&nbsp;           inventory\_docs=inventory\_docs,

&nbsp;           cost\_docs=cost\_docs,

&nbsp;           advisor\_docs=advisor\_docs,

&nbsp;       )



&nbsp;       findings = \[]

&nbsp;       for rule in self.rules:

&nbsp;           findings.extend(await rule.run(ctx))



&nbsp;       findings = rank\_findings(findings)

&nbsp;       docs = \[f.model\_dump() for f in findings]

&nbsp;       await self.findings\_repo.bulk\_upsert(subscription\_id, docs)



&nbsp;       return {

&nbsp;           "subscriptionId": subscription\_id,

&nbsp;           "scanId": scan\_id,

&nbsp;           "findingsCount": len(findings),

&nbsp;           "topFindingTitles": \[f.title for f in findings\[:5]],

&nbsp;       }

```



---



\# 14. Analysis entrypoint



\## `services/analysis/app/main.py`



```python

from \_\_future\_\_ import annotations



import asyncio

import json

import os



from services.analysis.app.orchestrator import AnalysisOrchestrator





async def \_main() -> None:

&nbsp;   raw = os.getenv("ACA\_ANALYSIS\_CONTEXT")

&nbsp;   if not raw:

&nbsp;       raise ValueError("ACA\_ANALYSIS\_CONTEXT env var is required")



&nbsp;   payload = json.loads(raw)

&nbsp;   subscription\_id = payload\["subscription\_id"]

&nbsp;   scan\_id = payload\["scan\_id"]



&nbsp;   orch = AnalysisOrchestrator()

&nbsp;   result = await orch.run(subscription\_id=subscription\_id, scan\_id=scan\_id)

&nbsp;   print(result)





if \_\_name\_\_ == "\_\_main\_\_":

&nbsp;   asyncio.run(\_main())

```



---



\# 15. Example API route later for findings



\## `services/api/app/routes/findings.py`



```python

from fastapi import APIRouter, HTTPException



router = APIRouter(prefix="/v1/findings", tags=\["findings"])





@router.get("/{subscription\_id}")

async def list\_findings(subscription\_id: str):

&nbsp;   # TODO wire FindingsRepo read model

&nbsp;   return {

&nbsp;       "subscriptionId": subscription\_id,

&nbsp;       "message": "Findings endpoint placeholder"

&nbsp;   }

```



---



\# 16. How the first Pareto engine works



This first version ranks using:



```text

priority score = annual savings × confidence ÷ implementation risk

```



That gives you the behavior you want:



\* high savings float to the top

\* high confidence increases priority

\* high implementation risk lowers priority



So ACA can produce outputs like:



```text

Top 10 actions to eliminate most Azure waste

```



That is exactly your Pareto vision.



---



\# 17. What this gives you immediately



With this phase, ACA can now produce real first findings:



\### Ghost resource findings



\* unattached disks

\* unattached public IPs



\### Operational optimization findings



\* dev/test night shutdown opportunities



\### Azure-native validation findings



\* high-impact Advisor cost recommendations



This is enough to start showing \*\*real product value\*\*.



---



\# 18. What to add next



The best next phase would be \*\*Phase 5: delivery pack\*\*:



\* script template registry

\* recommendation-to-script binding

\* Markdown / PDF report payload model

\* top findings summary

\* “Top 10 Azure Actions” export

\* customer-facing assessment package



That would make ACA output something sellable:



```text

Findings

→ scripts

→ assessment package

```



And that is very close to first-customer material.



If you want, I’ll do \*\*Phase 5: script templates + deliverables pack\*\* next.




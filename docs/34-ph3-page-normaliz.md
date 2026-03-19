Excellent. Here is \*\*Phase 3: real collector pagination + normalization pack\*\* for ACA.



This focuses on the parts that make the collector actually useful:



\* Resource Graph paging

\* Cost Management paging + `429` retry behavior

\* Advisor normalization

\* network/policy/activity collection structure

\* collector orchestration updates



I’m keeping it practical and close to your existing architecture.



---



\## `services/collector/app/utils/paging.py`



```python

from \_\_future\_\_ import annotations



from typing import Any





def extract\_next\_link(payload: dict\[str, Any]) -> str | None:

&nbsp;   return payload.get("nextLink") or payload.get("next\_link")





def extract\_rows\_and\_columns(payload: dict\[str, Any]) -> tuple\[list\[dict\[str, Any]], list\[str]]:

&nbsp;   """

&nbsp;   Cost Management query responses often come as:

&nbsp;   {

&nbsp;     "properties": {

&nbsp;       "columns": \[{"name": "PreTaxCost"}, ...],

&nbsp;       "rows": \[\[12.3, "rg1", ...], ...]

&nbsp;     }

&nbsp;   }

&nbsp;   """

&nbsp;   props = payload.get("properties", {})

&nbsp;   columns = \[c\["name"] for c in props.get("columns", \[])]

&nbsp;   rows = props.get("rows", \[])

&nbsp;   dict\_rows: list\[dict\[str, Any]] = \[]



&nbsp;   for row in rows:

&nbsp;       item = {}

&nbsp;       for idx, col in enumerate(columns):

&nbsp;           item\[col] = row\[idx] if idx < len(row) else None

&nbsp;       dict\_rows.append(item)



&nbsp;   return dict\_rows, columns

```



---



\## `services/collector/app/utils/http\_retry.py`



```python

from \_\_future\_\_ import annotations



import asyncio

from typing import Any, Awaitable, Callable, TypeVar



import httpx



T = TypeVar("T")





def \_retryable\_status(code: int) -> bool:

&nbsp;   return code in {408, 429, 500, 502, 503, 504}





async def retry\_http\_call(

&nbsp;   fn: Callable\[\[], Awaitable\[T]],

&nbsp;   retries: int = 6,

&nbsp;   base\_delay: float = 1.0,

) -> T:

&nbsp;   last\_exc: Exception | None = None



&nbsp;   for attempt in range(retries):

&nbsp;       try:

&nbsp;           return await fn()

&nbsp;       except httpx.HTTPStatusError as exc:

&nbsp;           last\_exc = exc

&nbsp;           code = exc.response.status\_code

&nbsp;           if not \_retryable\_status(code) or attempt == retries - 1:

&nbsp;               raise

&nbsp;           retry\_after = exc.response.headers.get("Retry-After")

&nbsp;           if retry\_after and retry\_after.isdigit():

&nbsp;               delay = float(retry\_after)

&nbsp;           else:

&nbsp;               delay = base\_delay \* (2 \*\* attempt)

&nbsp;           await asyncio.sleep(delay)

&nbsp;       except (httpx.ReadTimeout, httpx.ConnectTimeout, httpx.ConnectError) as exc:

&nbsp;           last\_exc = exc

&nbsp;           if attempt == retries - 1:

&nbsp;               raise

&nbsp;           await asyncio.sleep(base\_delay \* (2 \*\* attempt))



&nbsp;   if last\_exc:

&nbsp;       raise last\_exc

&nbsp;   raise RuntimeError("retry\_http\_call exhausted without exception")

```



---



\## `services/api/app/clients/azure\_rest.py` update



```python

from \_\_future\_\_ import annotations



from typing import Any



import httpx





class AzureRestClient:

&nbsp;   ARM\_BASE = "https://management.azure.com"



&nbsp;   def \_\_init\_\_(self, token: str) -> None:

&nbsp;       self.token = token



&nbsp;   @property

&nbsp;   def headers(self) -> dict\[str, str]:

&nbsp;       return {

&nbsp;           "Authorization": f"Bearer {self.token}",

&nbsp;           "Content-Type": "application/json",

&nbsp;       }



&nbsp;   async def get(self, path: str, params: dict | None = None) -> dict\[str, Any]:

&nbsp;       async with httpx.AsyncClient(timeout=90) as client:

&nbsp;           resp = await client.get(

&nbsp;               f"{self.ARM\_BASE}{path}",

&nbsp;               headers=self.headers,

&nbsp;               params=params,

&nbsp;           )

&nbsp;           resp.raise\_for\_status()

&nbsp;           return resp.json()



&nbsp;   async def post(self, path: str, json\_body: dict, params: dict | None = None) -> dict\[str, Any]:

&nbsp;       async with httpx.AsyncClient(timeout=90) as client:

&nbsp;           resp = await client.post(

&nbsp;               f"{self.ARM\_BASE}{path}",

&nbsp;               headers=self.headers,

&nbsp;               params=params,

&nbsp;               json=json\_body,

&nbsp;           )

&nbsp;           resp.raise\_for\_status()

&nbsp;           return resp.json()



&nbsp;   async def post\_absolute(self, url: str, json\_body: dict | None = None) -> dict\[str, Any]:

&nbsp;       async with httpx.AsyncClient(timeout=90) as client:

&nbsp;           resp = await client.post(

&nbsp;               url,

&nbsp;               headers=self.headers,

&nbsp;               json=json\_body,

&nbsp;           )

&nbsp;           resp.raise\_for\_status()

&nbsp;           return resp.json()



&nbsp;   async def get\_absolute(self, url: str) -> dict\[str, Any]:

&nbsp;       async with httpx.AsyncClient(timeout=90) as client:

&nbsp;           resp = await client.get(url, headers=self.headers)

&nbsp;           resp.raise\_for\_status()

&nbsp;           return resp.json()

```



---



\## `services/collector/app/normalizers/inventory\_normalizer.py`



```python

from \_\_future\_\_ import annotations



from typing import Any





def normalize\_inventory\_resource(subscription\_id: str, raw: dict\[str, Any]) -> dict\[str, Any]:

&nbsp;   return {

&nbsp;       "id": raw.get("id"),

&nbsp;       "subscriptionId": subscription\_id,

&nbsp;       "resourceId": raw.get("id"),

&nbsp;       "name": raw.get("name"),

&nbsp;       "type": raw.get("type"),

&nbsp;       "resourceGroup": raw.get("resourceGroup"),

&nbsp;       "location": raw.get("location"),

&nbsp;       "sku": raw.get("sku"),

&nbsp;       "kind": raw.get("kind"),

&nbsp;       "tags": raw.get("tags", {}),

&nbsp;       "raw": raw,

&nbsp;   }

```



---



\## `services/collector/app/normalizers/cost\_normalizer.py`



```python

from \_\_future\_\_ import annotations



import hashlib

from typing import Any





def \_hash\_resource\_id(resource\_id: str | None) -> str | None:

&nbsp;   if not resource\_id:

&nbsp;       return None

&nbsp;   return hashlib.sha256(resource\_id.encode("utf-8")).hexdigest()





def normalize\_cost\_row(subscription\_id: str, row: dict\[str, Any], hash\_resource\_ids: bool = False) -> dict\[str, Any]:

&nbsp;   resource\_id = (

&nbsp;       row.get("ResourceId")

&nbsp;       or row.get("resourceId")

&nbsp;       or row.get("InstanceId")

&nbsp;   )



&nbsp;   normalized\_resource\_id = \_hash\_resource\_id(resource\_id) if hash\_resource\_ids else resource\_id



&nbsp;   date\_value = row.get("UsageDate") or row.get("Date") or row.get("date")



&nbsp;   return {

&nbsp;       "id": f"{subscription\_id}:{date\_value}:{normalized\_resource\_id or row.get('ResourceGroup') or 'unknown'}",

&nbsp;       "subscriptionId": subscription\_id,

&nbsp;       "date": date\_value,

&nbsp;       "MeterCategory": row.get("MeterCategory"),

&nbsp;       "MeterName": row.get("MeterName"),

&nbsp;       "resourceGroup": row.get("ResourceGroup") or row.get("resourceGroup"),

&nbsp;       "resourceId": normalized\_resource\_id,

&nbsp;       "PreTaxCost": row.get("PreTaxCost"),

&nbsp;       "currency": row.get("Currency") or row.get("currency"),

&nbsp;       "raw": row,

&nbsp;   }

```



---



\## `services/collector/app/normalizers/advisor\_normalizer.py`



```python

from \_\_future\_\_ import annotations



from typing import Any





def normalize\_advisor\_recommendation(subscription\_id: str, raw: dict\[str, Any]) -> dict\[str, Any]:

&nbsp;   props = raw.get("properties", {})

&nbsp;   short\_desc = props.get("shortDescription", {})

&nbsp;   extended\_props = props.get("extendedProperties", {})



&nbsp;   return {

&nbsp;       "id": raw.get("id"),

&nbsp;       "subscriptionId": subscription\_id,

&nbsp;       "recommendationId": raw.get("name"),

&nbsp;       "resourceId": props.get("resourceMetadata", {}).get("resourceId"),

&nbsp;       "category": props.get("category"),

&nbsp;       "impact": props.get("impact"),

&nbsp;       "risk": props.get("risk"),

&nbsp;       "problem": short\_desc.get("problem"),

&nbsp;       "solution": short\_desc.get("solution"),

&nbsp;       "annualSavingsAmount": extended\_props.get("annualSavingsAmount"),

&nbsp;       "savingsCurrency": extended\_props.get("savingsCurrency"),

&nbsp;       "raw": raw,

&nbsp;   }

```



---



\## `services/collector/app/collectors/inventory.py` real paging version



```python

from \_\_future\_\_ import annotations



from app.clients.azure\_rest import AzureRestClient

from services.collector.app.normalizers.inventory\_normalizer import normalize\_inventory\_resource

from services.collector.app.utils.http\_retry import retry\_http\_call





class InventoryCollector:

&nbsp;   def \_\_init\_\_(self, writer) -> None:

&nbsp;       self.writer = writer



&nbsp;   async def collect(self, ctx, token: str) -> list\[dict]:

&nbsp;       client = AzureRestClient(token)

&nbsp;       all\_docs: list\[dict] = \[]

&nbsp;       skip\_token: str | None = None



&nbsp;       while True:

&nbsp;           body = {

&nbsp;               "subscriptions": \[ctx.subscription\_id],

&nbsp;               "query": """

&nbsp;                   Resources

&nbsp;                   | project id, name, type, resourceGroup, location, sku, kind, tags

&nbsp;               """.strip(),

&nbsp;               "options": {"resultFormat": "objectArray"},

&nbsp;           }

&nbsp;           if skip\_token:

&nbsp;               body\["options"]\["$skipToken"] = skip\_token



&nbsp;           async def \_call():

&nbsp;               return await client.post(

&nbsp;                   "/providers/Microsoft.ResourceGraph/resources",

&nbsp;                   json\_body=body,

&nbsp;                   params={"api-version": "2022-10-01"},

&nbsp;               )



&nbsp;           payload = await retry\_http\_call(\_call)

&nbsp;           rows = payload.get("data", \[])

&nbsp;           docs = \[normalize\_inventory\_resource(ctx.subscription\_id, row) for row in rows]

&nbsp;           all\_docs.extend(docs)



&nbsp;           skip\_token = payload.get("$skipToken")

&nbsp;           if not skip\_token:

&nbsp;               break



&nbsp;       await self.writer.bulk\_upsert("inventories", ctx.subscription\_id, all\_docs)

&nbsp;       return all\_docs

```



---



\## `services/collector/app/collectors/cost.py` real paging version



```python

from \_\_future\_\_ import annotations



from datetime import date, timedelta



from app.clients.azure\_rest import AzureRestClient

from services.collector.app.normalizers.cost\_normalizer import normalize\_cost\_row

from services.collector.app.utils.http\_retry import retry\_http\_call

from services.collector.app.utils.paging import extract\_rows\_and\_columns





class CostCollector:

&nbsp;   def \_\_init\_\_(self, writer, hash\_resource\_ids: bool = False) -> None:

&nbsp;       self.writer = writer

&nbsp;       self.hash\_resource\_ids = hash\_resource\_ids



&nbsp;   async def collect(self, ctx, token: str) -> list\[dict]:

&nbsp;       client = AzureRestClient(token)



&nbsp;       end\_date = date.today()

&nbsp;       start\_date = end\_date - timedelta(days=91)



&nbsp;       body = {

&nbsp;           "type": "ActualCost",

&nbsp;           "timeframe": "Custom",

&nbsp;           "timePeriod": {

&nbsp;               "from": f"{start\_date.isoformat()}T00:00:00Z",

&nbsp;               "to": f"{end\_date.isoformat()}T00:00:00Z",

&nbsp;           },

&nbsp;           "dataset": {

&nbsp;               "granularity": "Daily",

&nbsp;               "aggregation": {

&nbsp;                   "PreTaxCost": {"name": "PreTaxCost", "function": "Sum"}

&nbsp;               },

&nbsp;               "grouping": \[

&nbsp;                   {"type": "Dimension", "name": "MeterCategory"},

&nbsp;                   {"type": "Dimension", "name": "MeterName"},

&nbsp;                   {"type": "Dimension", "name": "ResourceGroup"},

&nbsp;                   {"type": "Dimension", "name": "ResourceId"},

&nbsp;                   {"type": "Dimension", "name": "Currency"},

&nbsp;                   {"type": "Dimension", "name": "UsageDate"},

&nbsp;               ],

&nbsp;           },

&nbsp;       }



&nbsp;       all\_docs: list\[dict] = \[]



&nbsp;       async def \_first\_call():

&nbsp;           return await client.post(

&nbsp;               f"/subscriptions/{ctx.subscription\_id}/providers/Microsoft.CostManagement/query",

&nbsp;               json\_body=body,

&nbsp;               params={"api-version": "2023-03-01"},

&nbsp;           )



&nbsp;       payload = await retry\_http\_call(\_first\_call)



&nbsp;       while True:

&nbsp;           rows, \_ = extract\_rows\_and\_columns(payload)

&nbsp;           docs = \[

&nbsp;               normalize\_cost\_row(

&nbsp;                   ctx.subscription\_id,

&nbsp;                   row,

&nbsp;                   hash\_resource\_ids=self.hash\_resource\_ids,

&nbsp;               )

&nbsp;               for row in rows

&nbsp;           ]

&nbsp;           all\_docs.extend(docs)



&nbsp;           next\_link = payload.get("properties", {}).get("nextLink")

&nbsp;           if not next\_link:

&nbsp;               break



&nbsp;           async def \_next\_call():

&nbsp;               return await client.post\_absolute(next\_link, json\_body=None)



&nbsp;           payload = await retry\_http\_call(\_next\_call)



&nbsp;       await self.writer.bulk\_upsert("cost-data", ctx.subscription\_id, all\_docs)

&nbsp;       return all\_docs

```



---



\## `services/collector/app/collectors/advisor.py` real collection version



```python

from \_\_future\_\_ import annotations



from app.clients.azure\_rest import AzureRestClient

from services.collector.app.normalizers.advisor\_normalizer import normalize\_advisor\_recommendation

from services.collector.app.utils.http\_retry import retry\_http\_call





class AdvisorCollector:

&nbsp;   def \_\_init\_\_(self, writer) -> None:

&nbsp;       self.writer = writer



&nbsp;   async def collect(self, ctx, token: str) -> list\[dict]:

&nbsp;       client = AzureRestClient(token)

&nbsp;       all\_docs: list\[dict] = \[]



&nbsp;       path = (

&nbsp;           f"/subscriptions/{ctx.subscription\_id}"

&nbsp;           "/providers/Microsoft.Advisor/recommendations"

&nbsp;       )



&nbsp;       async def \_first\_call():

&nbsp;           return await client.get(path, params={"api-version": "2023-01-01"})



&nbsp;       payload = await retry\_http\_call(\_first\_call)



&nbsp;       while True:

&nbsp;           rows = payload.get("value", \[])

&nbsp;           docs = \[normalize\_advisor\_recommendation(ctx.subscription\_id, row) for row in rows]

&nbsp;           all\_docs.extend(docs)



&nbsp;           next\_link = payload.get("nextLink")

&nbsp;           if not next\_link:

&nbsp;               break



&nbsp;           async def \_next\_call():

&nbsp;               return await client.get\_absolute(next\_link)



&nbsp;           payload = await retry\_http\_call(\_next\_call)



&nbsp;       await self.writer.bulk\_upsert("advisor", ctx.subscription\_id, all\_docs)

&nbsp;       return all\_docs

```



---



\## `services/collector/app/collectors/policy.py` better summary version



```python

from \_\_future\_\_ import annotations



from app.clients.azure\_rest import AzureRestClient

from services.collector.app.utils.http\_retry import retry\_http\_call





class PolicyCollector:

&nbsp;   async def collect(self, ctx, token: str) -> dict:

&nbsp;       client = AzureRestClient(token)



&nbsp;       body = {

&nbsp;           "query": """

&nbsp;               PolicyResources

&nbsp;               | summarize nonCompliant=countif(ComplianceState == 'NonCompliant'),

&nbsp;                           compliant=countif(ComplianceState == 'Compliant')

&nbsp;           """.strip()

&nbsp;       }



&nbsp;       async def \_call():

&nbsp;           return await client.post(

&nbsp;               f"/subscriptions/{ctx.subscription\_id}/providers/Microsoft.PolicyInsights/policyStates/latest/queryResults",

&nbsp;               json\_body=body,

&nbsp;               params={"api-version": "2022-04-01"},

&nbsp;           )



&nbsp;       payload = await retry\_http\_call(\_call)

&nbsp;       rows = payload.get("value", \[])

&nbsp;       if not rows:

&nbsp;           return {

&nbsp;               "policySignalsCount": 0,

&nbsp;               "policySummary": {"compliant": 0, "nonCompliant": 0},

&nbsp;           }



&nbsp;       row = rows\[0]

&nbsp;       return {

&nbsp;           "policySignalsCount": int((row.get("compliant") or 0) + (row.get("nonCompliant") or 0)),

&nbsp;           "policySummary": {

&nbsp;               "compliant": row.get("compliant", 0),

&nbsp;               "nonCompliant": row.get("nonCompliant", 0),

&nbsp;           },

&nbsp;       }

```



---



\## `services/collector/app/collectors/network.py` light topology version



```python

from \_\_future\_\_ import annotations



from app.clients.azure\_rest import AzureRestClient

from services.collector.app.utils.http\_retry import retry\_http\_call





class NetworkCollector:

&nbsp;   async def collect(self, ctx, token: str) -> dict:

&nbsp;       client = AzureRestClient(token)



&nbsp;       async def \_call():

&nbsp;           return await client.get(

&nbsp;               f"/subscriptions/{ctx.subscription\_id}/resources",

&nbsp;               params={

&nbsp;                   "api-version": "2021-04-01",

&nbsp;                   "$filter": "resourceType eq 'Microsoft.Network/publicIPAddresses' or "

&nbsp;                              "resourceType eq 'Microsoft.Network/networkSecurityGroups' or "

&nbsp;                              "resourceType eq 'Microsoft.Network/virtualNetworks'",

&nbsp;               },

&nbsp;           )



&nbsp;       payload = await retry\_http\_call(\_call)

&nbsp;       rows = payload.get("value", \[])



&nbsp;       public\_ip\_count = sum(1 for r in rows if r.get("type") == "Microsoft.Network/publicIPAddresses")

&nbsp;       nsg\_count = sum(1 for r in rows if r.get("type") == "Microsoft.Network/networkSecurityGroups")

&nbsp;       vnet\_count = sum(1 for r in rows if r.get("type") == "Microsoft.Network/virtualNetworks")



&nbsp;       return {

&nbsp;           "networkSignalsCount": len(rows),

&nbsp;           "networkSummary": {

&nbsp;               "publicIpCount": public\_ip\_count,

&nbsp;               "nsgCount": nsg\_count,

&nbsp;               "vnetCount": vnet\_count,

&nbsp;           },

&nbsp;       }

```



---



\## `services/collector/app/collectors/activity.py` starter version



```python

from \_\_future\_\_ import annotations



from app.clients.azure\_rest import AzureRestClient

from services.collector.app.utils.http\_retry import retry\_http\_call





class ActivityCollector:

&nbsp;   async def collect(self, ctx, token: str) -> dict:

&nbsp;       client = AzureRestClient(token)



&nbsp;       async def \_call():

&nbsp;           return await client.get(

&nbsp;               f"/subscriptions/{ctx.subscription\_id}/providers/microsoft.insights/eventtypes/management/values",

&nbsp;               params={

&nbsp;                   "api-version": "2015-04-01",

&nbsp;                   "$filter": "eventTimestamp ge '2026-01-01T00:00:00Z' and eventTimestamp le '2026-01-02T00:00:00Z'",

&nbsp;               },

&nbsp;           )



&nbsp;       payload = await retry\_http\_call(\_call)

&nbsp;       rows = payload.get("value", \[])



&nbsp;       return {

&nbsp;           "activitySignalsCount": len(rows),

&nbsp;       }

```



---



\## `services/collector/app/orchestrator.py` token-aware update



```python

from \_\_future\_\_ import annotations



from app.clients.azure\_token\_provider import AzureTokenProvider

from app.repos.advisor\_repo import AdvisorRepo

from app.repos.cost\_data\_repo import CostDataRepo

from app.repos.inventories\_repo import InventoriesRepo

from app.repos.scans\_repo import ScansRepo

from services.collector.app.collectors.activity import ActivityCollector

from services.collector.app.collectors.advisor import AdvisorCollector

from services.collector.app.collectors.cost import CostCollector

from services.collector.app.collectors.inventory import InventoryCollector

from services.collector.app.collectors.network import NetworkCollector

from services.collector.app.collectors.policy import PolicyCollector

from services.collector.app.writers.cosmos\_writer import CosmosWriter





class CollectorOrchestrator:

&nbsp;   def \_\_init\_\_(self) -> None:

&nbsp;       self.scans\_repo = ScansRepo()

&nbsp;       writer = CosmosWriter()



&nbsp;       self.inventory = InventoryCollector(writer)

&nbsp;       self.cost = CostCollector(writer, hash\_resource\_ids=False)

&nbsp;       self.advisor = AdvisorCollector(writer)

&nbsp;       self.policy = PolicyCollector()

&nbsp;       self.network = NetworkCollector()

&nbsp;       self.activity = ActivityCollector()

&nbsp;       self.token\_provider = AzureTokenProvider()



&nbsp;   async def run(self, ctx) -> None:

&nbsp;       await self.scans\_repo.update\_scan(

&nbsp;           ctx.scan\_id,

&nbsp;           ctx.subscription\_id,

&nbsp;           status="running",

&nbsp;       )



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

&nbsp;           token = await self.token\_provider.get\_arm\_token(

&nbsp;               mode=ctx.auth\_mode,

&nbsp;               tenant\_id=ctx.tenant\_id,

&nbsp;               user\_assertion=None,

&nbsp;           )



&nbsp;           inventory\_docs = await self.inventory.collect(ctx, token)

&nbsp;           stats\["inventoryCount"] = len(inventory\_docs)



&nbsp;           if ctx.extraction\_depth in {

&nbsp;               "DEPTH\_2\_INVENTORY\_COST",

&nbsp;               "DEPTH\_3\_STANDARD",

&nbsp;               "DEPTH\_4\_ENHANCED",

&nbsp;               "DEPTH\_5\_ACTIVITY\_ENHANCED",

&nbsp;           }:

&nbsp;               cost\_docs = await self.cost.collect(ctx, token)

&nbsp;               stats\["costRows"] = len(cost\_docs)



&nbsp;           if ctx.extraction\_depth in {

&nbsp;               "DEPTH\_3\_STANDARD",

&nbsp;               "DEPTH\_4\_ENHANCED",

&nbsp;               "DEPTH\_5\_ACTIVITY\_ENHANCED",

&nbsp;           }:

&nbsp;               advisor\_docs = await self.advisor.collect(ctx, token)

&nbsp;               stats\["advisorRecs"] = len(advisor\_docs)



&nbsp;           if ctx.extraction\_depth in {"DEPTH\_4\_ENHANCED", "DEPTH\_5\_ACTIVITY\_ENHANCED"}:

&nbsp;               policy\_stats = await self.policy.collect(ctx, token)

&nbsp;               network\_stats = await self.network.collect(ctx, token)

&nbsp;               stats.update(policy\_stats)

&nbsp;               stats.update(network\_stats)



&nbsp;           if ctx.extraction\_depth == "DEPTH\_5\_ACTIVITY\_ENHANCED":

&nbsp;               activity\_stats = await self.activity.collect(ctx, token)

&nbsp;               stats.update(activity\_stats)



&nbsp;           await self.scans\_repo.update\_scan(

&nbsp;               ctx.scan\_id,

&nbsp;               ctx.subscription\_id,

&nbsp;               status="collected",

&nbsp;               \*\*stats,

&nbsp;           )



&nbsp;           # later: trigger analysis job

&nbsp;           await self.scans\_repo.update\_scan(

&nbsp;               ctx.scan\_id,

&nbsp;               ctx.subscription\_id,

&nbsp;               status="succeeded",

&nbsp;               \*\*stats,

&nbsp;           )



&nbsp;       except Exception as exc:

&nbsp;           stats\["errorsCount"] += 1

&nbsp;           await self.scans\_repo.update\_scan(

&nbsp;               ctx.scan\_id,

&nbsp;               ctx.subscription\_id,

&nbsp;               status="failed",

&nbsp;               error=str(exc),

&nbsp;               \*\*stats,

&nbsp;           )

&nbsp;           raise

```



---



\## `services/collector/app/main.py`



```python

from \_\_future\_\_ import annotations



import asyncio

import json

import os



from services.collector.app.job\_context import JobContext

from services.collector.app.orchestrator import CollectorOrchestrator





async def \_main() -> None:

&nbsp;   raw = os.getenv("ACA\_JOB\_CONTEXT")

&nbsp;   if not raw:

&nbsp;       raise ValueError("ACA\_JOB\_CONTEXT env var is required")



&nbsp;   ctx = JobContext(\*\*json.loads(raw))

&nbsp;   orch = CollectorOrchestrator()

&nbsp;   await orch.run(ctx)





if \_\_name\_\_ == "\_\_main\_\_":

&nbsp;   asyncio.run(\_main())

```



---



\## Suggested improvements to `ScanService.trigger\_collector\_job()`



```python

import json

import os



from azure.identity.aio import DefaultAzureCredential

from azure.mgmt.appcontainers import ContainerAppsAPIClient





class ScanService:

&nbsp;   ...



&nbsp;   async def trigger\_collector\_job(self, scan\_id: str, scan\_doc: dict) -> None:

&nbsp;       subscription\_id = os.getenv("ACA\_INFRA\_SUBSCRIPTION\_ID", "")

&nbsp;       resource\_group = os.getenv("ACA\_INFRA\_RESOURCE\_GROUP", "")

&nbsp;       job\_name = os.getenv("ACA\_COLLECTOR\_JOB\_NAME", "")



&nbsp;       credential = DefaultAzureCredential()

&nbsp;       client = ContainerAppsAPIClient(credential, subscription\_id)



&nbsp;       env\_vars = \[

&nbsp;           {

&nbsp;               "name": "ACA\_JOB\_CONTEXT",

&nbsp;               "value": json.dumps(

&nbsp;                   {

&nbsp;                       "scan\_id": scan\_doc\["scan\_id"],

&nbsp;                       "subscription\_id": scan\_doc\["subscription\_id"],

&nbsp;                       "tenant\_id": scan\_doc.get("tenant\_id"),

&nbsp;                       "auth\_mode": scan\_doc.get("preflight", {}).get("mode", "delegated"),

&nbsp;                       "extraction\_depth": scan\_doc.get("preflight", {}).get("extraction\_depth", {}).get("level", "DEPTH\_0\_NONE"),

&nbsp;                       "actor\_id": "api-trigger",

&nbsp;                   }

&nbsp;               ),

&nbsp;           }

&nbsp;       ]



&nbsp;       # NOTE:

&nbsp;       # exact SDK call shape may vary with SDK version.

&nbsp;       # Keep this as a Copilot implementation target and verify against installed SDK.

&nbsp;       await client.jobs.begin\_start(

&nbsp;           resource\_group\_name=resource\_group,

&nbsp;           job\_name=job\_name,

&nbsp;           template={"containers": \[{"env": env\_vars}]},

&nbsp;       )

```



---



\## Two important notes for Copilot



\### 1. Cost Management pagination



Cost Management next-page behavior is not as uniform as classic ARM list APIs. In practice, your collector should support:



\* initial `query` POST

\* `properties.nextLink` continuation if returned

\* retry for `429`

\* safe partial-failure reporting



That aligns with the ACA plan that explicitly calls out 91-day daily extraction and throttling backoff. 



\### 2. Resource Graph skip tokens



Resource Graph may return `$skipToken` rather than `nextLink`, so the inventory collector should keep the current loop approach and reuse the same query with updated `options.$skipToken`.



---



\## What this phase gives you



Now you have:



\* \*\*real Azure REST-based probe skeletons\*\*

\* \*\*real collector pagination patterns\*\*

\* \*\*normalizers for inventory, cost, Advisor\*\*

\* \*\*Cosmos repo implementations\*\*

\* \*\*token-aware orchestrator\*\*

\* \*\*job entrypoint\*\*

\* a clear path from:



&nbsp; \* pre-flight

&nbsp; \* to collection

&nbsp; \* to persisted raw material for ACA rules



This matches your ACA design where the collector gathers inventory, cost, Advisor, optional policy/activity signals, writes them to Cosmos, and feeds the later 12-rule Pareto analysis engine.



The next best move is \*\*Phase 4: analysis engine starter pack\*\*:



\* findings models

\* rule contracts

\* Pareto scoring

\* ghost resource and night shutdown rules

\* findings persistence



That would turn collected data into the first real ACA recommendations.




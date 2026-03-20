Perfect. The next useful step is the \*\*real Cosmos repo implementation + Azure probe skeletons\*\* so Copilot can stop scaffolding and start wiring real ACA behavior. This fits your current architecture: FastAPI API service, collector job, read-only Azure SDK calls, Cosmos containers partitioned by `subscriptionId`, and the five baseline pre-flight probes plus optional policy/activity checks.



Below is a starter pack.



---



\## `services/api/app/repos/cosmos\_base.py`



```python

from \_\_future\_\_ import annotations



import os

from typing import Any, Iterable



from azure.cosmos.aio import CosmosClient

from azure.cosmos import PartitionKey

from azure.identity.aio import DefaultAzureCredential





class CosmosClientFactory:

&nbsp;   """

&nbsp;   Supports:

&nbsp;   1) Account endpoint + key

&nbsp;   2) Account endpoint + Managed Identity / Entra auth

&nbsp;   """



&nbsp;   def \_\_init\_\_(self) -> None:

&nbsp;       self.endpoint = os.getenv("COSMOS\_ENDPOINT", "")

&nbsp;       self.key = os.getenv("COSMOS\_KEY", "")

&nbsp;       self.database\_name = os.getenv("COSMOS\_DATABASE\_NAME", "aca")



&nbsp;   async def create\_client(self) -> CosmosClient:

&nbsp;       if not self.endpoint:

&nbsp;           raise ValueError("COSMOS\_ENDPOINT is required")



&nbsp;       if self.key:

&nbsp;           return CosmosClient(self.endpoint, credential=self.key)



&nbsp;       credential = DefaultAzureCredential()

&nbsp;       return CosmosClient(self.endpoint, credential=credential)



&nbsp;   async def get\_database\_client(self):

&nbsp;       client = await self.create\_client()

&nbsp;       return client.get\_database\_client(self.database\_name)





class CosmosContainerHelper:

&nbsp;   def \_\_init\_\_(self, database\_client, container\_name: str) -> None:

&nbsp;       self.database\_client = database\_client

&nbsp;       self.container\_name = container\_name



&nbsp;   async def get\_container(self):

&nbsp;       return self.database\_client.get\_container\_client(self.container\_name)



&nbsp;   async def ensure\_container(

&nbsp;       self,

&nbsp;       partition\_key\_path: str,

&nbsp;       throughput: int | None = None,

&nbsp;   ):

&nbsp;       return await self.database\_client.create\_container\_if\_not\_exists(

&nbsp;           id=self.container\_name,

&nbsp;           partition\_key=PartitionKey(path=partition\_key\_path),

&nbsp;           offer\_throughput=throughput,

&nbsp;       )





async def bulk\_upsert\_items(container, items: Iterable\[dict\[str, Any]]) -> int:

&nbsp;   count = 0

&nbsp;   for item in items:

&nbsp;       await container.upsert\_item(item)

&nbsp;       count += 1

&nbsp;   return count

```



---



\## `services/api/app/repos/scans\_repo.py`



```python

from \_\_future\_\_ import annotations



from typing import Any



from app.repos.cosmos\_base import CosmosClientFactory, CosmosContainerHelper





class ScansRepo:

&nbsp;   CONTAINER = "scans"



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



&nbsp;   async def upsert\_scan(self, doc: dict\[str, Any]) -> dict\[str, Any]:

&nbsp;       container = await self.\_container()

&nbsp;       await container.upsert\_item(doc)

&nbsp;       return doc



&nbsp;   async def get\_scan(self, scan\_id: str, subscription\_id: str) -> dict\[str, Any] | None:

&nbsp;       container = await self.\_container()

&nbsp;       try:

&nbsp;           return await container.read\_item(item=scan\_id, partition\_key=subscription\_id)

&nbsp;       except Exception:

&nbsp;           return None



&nbsp;   async def update\_scan(self, scan\_id: str, subscription\_id: str, \*\*fields: Any) -> dict\[str, Any] | None:

&nbsp;       doc = await self.get\_scan(scan\_id, subscription\_id)

&nbsp;       if not doc:

&nbsp;           return None

&nbsp;       doc.update(fields)

&nbsp;       await self.upsert\_scan(doc)

&nbsp;       return doc



&nbsp;   async def query\_scan\_by\_id(self, scan\_id: str, subscription\_id: str) -> dict\[str, Any] | None:

&nbsp;       """

&nbsp;       Useful if id strategy ever changes and read\_item is not sufficient.

&nbsp;       """

&nbsp;       container = await self.\_container()

&nbsp;       query = "SELECT \* FROM c WHERE c.scan\_id = @scan\_id"

&nbsp;       params = \[{"name": "@scan\_id", "value": scan\_id}]

&nbsp;       items = container.query\_items(

&nbsp;           query=query,

&nbsp;           parameters=params,

&nbsp;           partition\_key=subscription\_id,

&nbsp;       )

&nbsp;       async for item in items:

&nbsp;           return item

&nbsp;       return None

```



---



\## `services/api/app/repos/inventories\_repo.py`



```python

from \_\_future\_\_ import annotations



from app.repos.cosmos\_base import CosmosClientFactory, CosmosContainerHelper, bulk\_upsert\_items





class InventoriesRepo:

&nbsp;   CONTAINER = "inventories"



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



\## `services/api/app/repos/cost\_data\_repo.py`



```python

from \_\_future\_\_ import annotations



from app.repos.cosmos\_base import CosmosClientFactory, CosmosContainerHelper, bulk\_upsert\_items





class CostDataRepo:

&nbsp;   CONTAINER = "cost-data"



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



\## `services/api/app/repos/advisor\_repo.py`



```python

from \_\_future\_\_ import annotations



from app.repos.cosmos\_base import CosmosClientFactory, CosmosContainerHelper, bulk\_upsert\_items





class AdvisorRepo:

&nbsp;   CONTAINER = "advisor"



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



\## `services/api/app/clients/azure\_token\_provider.py`



```python

from \_\_future\_\_ import annotations



import os

from typing import Optional



from azure.identity.aio import (

&nbsp;   ClientSecretCredential,

&nbsp;   DefaultAzureCredential,

&nbsp;   OnBehalfOfCredential,

)





class AzureTokenProvider:

&nbsp;   """

&nbsp;   Supports:

&nbsp;   - delegated / OBO

&nbsp;   - service principal

&nbsp;   - managed identity / default

&nbsp;   """



&nbsp;   ARM\_SCOPE = "https://management.azure.com/.default"



&nbsp;   async def get\_credential(

&nbsp;       self,

&nbsp;       mode: str,

&nbsp;       tenant\_id: Optional\[str] = None,

&nbsp;       user\_assertion: Optional\[str] = None,

&nbsp;   ):

&nbsp;       if mode == "service\_principal":

&nbsp;           client\_id = os.getenv("ACA\_SP\_CLIENT\_ID", "")

&nbsp;           client\_secret = os.getenv("ACA\_SP\_CLIENT\_SECRET", "")

&nbsp;           tenant\_id = tenant\_id or os.getenv("ACA\_SP\_TENANT\_ID", "")

&nbsp;           if not all(\[client\_id, client\_secret, tenant\_id]):

&nbsp;               raise ValueError("Service principal credentials are incomplete")

&nbsp;           return ClientSecretCredential(

&nbsp;               tenant\_id=tenant\_id,

&nbsp;               client\_id=client\_id,

&nbsp;               client\_secret=client\_secret,

&nbsp;           )



&nbsp;       if mode == "delegated":

&nbsp;           # OBO pattern for API receiving user token

&nbsp;           tenant\_id = tenant\_id or os.getenv("ACA\_OBO\_TENANT\_ID", "common")

&nbsp;           client\_id = os.getenv("ACA\_OBO\_CLIENT\_ID", "")

&nbsp;           client\_secret = os.getenv("ACA\_OBO\_CLIENT\_SECRET", "")

&nbsp;           if not all(\[client\_id, client\_secret, user\_assertion]):

&nbsp;               raise ValueError("Delegated OBO credentials are incomplete")

&nbsp;           return OnBehalfOfCredential(

&nbsp;               tenant\_id=tenant\_id,

&nbsp;               client\_id=client\_id,

&nbsp;               client\_secret=client\_secret,

&nbsp;               user\_assertion=user\_assertion,

&nbsp;           )



&nbsp;       # lighthouse / managed identity / default case

&nbsp;       return DefaultAzureCredential()



&nbsp;   async def get\_arm\_token(

&nbsp;       self,

&nbsp;       mode: str,

&nbsp;       tenant\_id: Optional\[str] = None,

&nbsp;       user\_assertion: Optional\[str] = None,

&nbsp;   ) -> str:

&nbsp;       credential = await self.get\_credential(

&nbsp;           mode=mode,

&nbsp;           tenant\_id=tenant\_id,

&nbsp;           user\_assertion=user\_assertion,

&nbsp;       )

&nbsp;       token = await credential.get\_token(self.ARM\_SCOPE)

&nbsp;       return token.token

```



---



\## `services/api/app/clients/azure\_rest.py`



```python

from \_\_future\_\_ import annotations



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



&nbsp;   async def get(self, path: str, params: dict | None = None) -> dict:

&nbsp;       async with httpx.AsyncClient(timeout=60) as client:

&nbsp;           resp = await client.get(f"{self.ARM\_BASE}{path}", headers=self.headers, params=params)

&nbsp;           resp.raise\_for\_status()

&nbsp;           return resp.json()



&nbsp;   async def post(self, path: str, json\_body: dict, params: dict | None = None) -> dict:

&nbsp;       async with httpx.AsyncClient(timeout=60) as client:

&nbsp;           resp = await client.post(

&nbsp;               f"{self.ARM\_BASE}{path}",

&nbsp;               headers=self.headers,

&nbsp;               params=params,

&nbsp;               json=json\_body,

&nbsp;           )

&nbsp;           resp.raise\_for\_status()

&nbsp;           return resp.json()

```



---



\## `services/collector/app/probes/auth\_probe.py`



```python

from \_\_future\_\_ import annotations



from app.models.preflight import ProbeResult

from app.clients.azure\_token\_provider import AzureTokenProvider





class AuthProbe:

&nbsp;   def \_\_init\_\_(self) -> None:

&nbsp;       self.provider = AzureTokenProvider()



&nbsp;   async def run(self, mode: str, tenant\_id: str | None = None, user\_assertion: str | None = None) -> tuple\[ProbeResult, str | None]:

&nbsp;       try:

&nbsp;           token = await self.provider.get\_arm\_token(

&nbsp;               mode=mode,

&nbsp;               tenant\_id=tenant\_id,

&nbsp;               user\_assertion=user\_assertion,

&nbsp;           )

&nbsp;           return (

&nbsp;               ProbeResult(

&nbsp;                   probe\_name="arm\_auth",

&nbsp;                   status="PASS",

&nbsp;                   required\_role\_or\_permission="Valid ARM token",

&nbsp;                   actual\_result="ARM token acquired successfully",

&nbsp;               ),

&nbsp;               token,

&nbsp;           )

&nbsp;       except Exception as exc:

&nbsp;           return (

&nbsp;               ProbeResult(

&nbsp;                   probe\_name="arm\_auth",

&nbsp;                   status="FAIL",

&nbsp;                   required\_role\_or\_permission="Valid ARM token",

&nbsp;                   actual\_result="Failed to acquire ARM token",

&nbsp;                   error\_code=type(exc).\_\_name\_\_,

&nbsp;                   human\_guidance="Verify sign-in mode, tenant, and token exchange configuration.",

&nbsp;                   can\_continue\_without\_this=False,

&nbsp;                   collection\_impact="Collection cannot start.",

&nbsp;               ),

&nbsp;               None,

&nbsp;           )

```



---



\## `services/collector/app/probes/resource\_graph\_probe.py`



```python

from \_\_future\_\_ import annotations



from app.models.preflight import ProbeResult

from app.clients.azure\_rest import AzureRestClient





class ResourceGraphProbe:

&nbsp;   async def run(self, token: str, subscription\_id: str) -> ProbeResult:

&nbsp;       client = AzureRestClient(token)

&nbsp;       body = {

&nbsp;           "subscriptions": \[subscription\_id],

&nbsp;           "query": "Resources | project id, name, type | limit 1",

&nbsp;       }

&nbsp;       try:

&nbsp;           await client.post(

&nbsp;               "/providers/Microsoft.ResourceGraph/resources",

&nbsp;               json\_body=body,

&nbsp;               params={"api-version": "2022-10-01"},

&nbsp;           )

&nbsp;           return ProbeResult(

&nbsp;               probe\_name="resource\_graph",

&nbsp;               status="PASS",

&nbsp;               required\_role\_or\_permission="Reader + Resource Graph query",

&nbsp;               actual\_result="Resource Graph query succeeded",

&nbsp;           )

&nbsp;       except Exception as exc:

&nbsp;           return ProbeResult(

&nbsp;               probe\_name="resource\_graph",

&nbsp;               status="FAIL",

&nbsp;               required\_role\_or\_permission="Reader + Resource Graph query",

&nbsp;               actual\_result="Resource Graph query failed",

&nbsp;               error\_code=type(exc).\_\_name\_\_,

&nbsp;               human\_guidance="Grant Reader access at subscription scope and verify Resource Graph availability.",

&nbsp;               can\_continue\_without\_this=False,

&nbsp;               collection\_impact="Inventory extraction unavailable.",

&nbsp;           )

```



---



\## `services/collector/app/probes/reader\_probe.py`



```python

from \_\_future\_\_ import annotations



from app.models.preflight import ProbeResult

from app.clients.azure\_rest import AzureRestClient





class ReaderProbe:

&nbsp;   async def run(self, token: str, subscription\_id: str) -> ProbeResult:

&nbsp;       client = AzureRestClient(token)

&nbsp;       try:

&nbsp;           await client.get(

&nbsp;               f"/subscriptions/{subscription\_id}",

&nbsp;               params={"api-version": "2020-01-01"},

&nbsp;           )

&nbsp;           return ProbeResult(

&nbsp;               probe\_name="subscription\_reader",

&nbsp;               status="PASS",

&nbsp;               required\_role\_or\_permission="Reader",

&nbsp;               actual\_result="Subscription metadata is readable",

&nbsp;           )

&nbsp;       except Exception as exc:

&nbsp;           return ProbeResult(

&nbsp;               probe\_name="subscription\_reader",

&nbsp;               status="FAIL",

&nbsp;               required\_role\_or\_permission="Reader",

&nbsp;               actual\_result="Subscription metadata is not readable",

&nbsp;               error\_code=type(exc).\_\_name\_\_,

&nbsp;               human\_guidance="Grant Reader at subscription scope.",

&nbsp;               can\_continue\_without\_this=False,

&nbsp;               collection\_impact="Collector cannot reliably read inventory.",

&nbsp;           )

```



---



\## `services/collector/app/probes/cost\_probe.py`



```python

from \_\_future\_\_ import annotations



from datetime import date, timedelta



from app.models.preflight import ProbeResult

from app.clients.azure\_rest import AzureRestClient





class CostProbe:

&nbsp;   async def run(self, token: str, subscription\_id: str) -> ProbeResult:

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

&nbsp;                   "totalCost": {"name": "PreTaxCost", "function": "Sum"}

&nbsp;               },

&nbsp;           },

&nbsp;       }



&nbsp;       try:

&nbsp;           await client.post(

&nbsp;               f"/subscriptions/{subscription\_id}/providers/Microsoft.CostManagement/query",

&nbsp;               json\_body=body,

&nbsp;               params={"api-version": "2023-03-01"},

&nbsp;           )

&nbsp;           return ProbeResult(

&nbsp;               probe\_name="cost\_management",

&nbsp;               status="PASS",

&nbsp;               required\_role\_or\_permission="Cost Management Reader",

&nbsp;               actual\_result="Cost Management query succeeded for 91-day window",

&nbsp;           )

&nbsp;       except Exception as exc:

&nbsp;           return ProbeResult(

&nbsp;               probe\_name="cost\_management",

&nbsp;               status="FAIL",

&nbsp;               required\_role\_or\_permission="Cost Management Reader",

&nbsp;               actual\_result="Cost Management query failed",

&nbsp;               error\_code=type(exc).\_\_name\_\_,

&nbsp;               human\_guidance="Grant Cost Management Reader at subscription scope.",

&nbsp;               can\_continue\_without\_this=False,

&nbsp;               collection\_impact="Cost-based analysis cannot proceed.",

&nbsp;           )

```



---



\## `services/collector/app/probes/advisor\_probe.py`



```python

from \_\_future\_\_ import annotations



from app.models.preflight import ProbeResult

from app.clients.azure\_rest import AzureRestClient





class AdvisorProbe:

&nbsp;   async def run(self, token: str, subscription\_id: str) -> ProbeResult:

&nbsp;       client = AzureRestClient(token)

&nbsp;       try:

&nbsp;           await client.get(

&nbsp;               f"/subscriptions/{subscription\_id}/providers/Microsoft.Advisor/recommendations",

&nbsp;               params={"api-version": "2023-01-01"},

&nbsp;           )

&nbsp;           return ProbeResult(

&nbsp;               probe\_name="advisor",

&nbsp;               status="PASS",

&nbsp;               required\_role\_or\_permission="Advisor Reader / recommendation read",

&nbsp;               actual\_result="Advisor recommendations accessible",

&nbsp;           )

&nbsp;       except Exception as exc:

&nbsp;           return ProbeResult(

&nbsp;               probe\_name="advisor",

&nbsp;               status="FAIL",

&nbsp;               required\_role\_or\_permission="Advisor Reader / recommendation read",

&nbsp;               actual\_result="Advisor recommendations unavailable",

&nbsp;               error\_code=type(exc).\_\_name\_\_,

&nbsp;               human\_guidance="Ensure Advisor recommendation read access is available.",

&nbsp;               can\_continue\_without\_this=False,

&nbsp;               collection\_impact="Standard ACA scan cannot proceed.",

&nbsp;           )

```



---



\## `services/collector/app/probes/policy\_probe.py`



```python

from \_\_future\_\_ import annotations



from app.models.preflight import ProbeResult

from app.clients.azure\_rest import AzureRestClient





class PolicyProbe:

&nbsp;   async def run(self, token: str, subscription\_id: str) -> ProbeResult:

&nbsp;       client = AzureRestClient(token)

&nbsp;       try:

&nbsp;           await client.post(

&nbsp;               f"/subscriptions/{subscription\_id}/providers/Microsoft.PolicyInsights/policyStates/latest/queryResults",

&nbsp;               json\_body={"query": "SELECT TOP 1 \*"},

&nbsp;               params={"api-version": "2022-04-01"},

&nbsp;           )

&nbsp;           return ProbeResult(

&nbsp;               probe\_name="policy",

&nbsp;               status="PASS",

&nbsp;               required\_role\_or\_permission="Policy Insights Reader",

&nbsp;               actual\_result="Policy Insights accessible",

&nbsp;               can\_continue\_without\_this=True,

&nbsp;           )

&nbsp;       except Exception as exc:

&nbsp;           return ProbeResult(

&nbsp;               probe\_name="policy",

&nbsp;               status="WARN",

&nbsp;               required\_role\_or\_permission="Policy Insights Reader",

&nbsp;               actual\_result="Policy Insights unavailable",

&nbsp;               error\_code=type(exc).\_\_name\_\_,

&nbsp;               human\_guidance="Policy-based findings will be skipped.",

&nbsp;               can\_continue\_without\_this=True,

&nbsp;               collection\_impact="Reduced governance/policy finding coverage.",

&nbsp;           )

```



---



\## `services/collector/app/probes/activity\_probe.py`



```python

from \_\_future\_\_ import annotations



from app.models.preflight import ProbeResult

from app.clients.azure\_rest import AzureRestClient





class ActivityProbe:

&nbsp;   async def run(self, token: str, subscription\_id: str) -> ProbeResult:

&nbsp;       client = AzureRestClient(token)

&nbsp;       try:

&nbsp;           await client.get(

&nbsp;               f"/subscriptions/{subscription\_id}/providers/microsoft.insights/eventtypes/management/values",

&nbsp;               params={

&nbsp;                   "api-version": "2015-04-01",

&nbsp;                   "$filter": "eventTimestamp ge '2026-01-01T00:00:00Z' and eventTimestamp le '2026-01-02T00:00:00Z'",

&nbsp;               },

&nbsp;           )

&nbsp;           return ProbeResult(

&nbsp;               probe\_name="activity",

&nbsp;               status="PASS",

&nbsp;               required\_role\_or\_permission="Activity Log / Log Analytics Reader",

&nbsp;               actual\_result="Activity source accessible",

&nbsp;               can\_continue\_without\_this=True,

&nbsp;           )

&nbsp;       except Exception as exc:

&nbsp;           return ProbeResult(

&nbsp;               probe\_name="activity",

&nbsp;               status="WARN",

&nbsp;               required\_role\_or\_permission="Activity Log / Log Analytics Reader",

&nbsp;               actual\_result="Activity source unavailable",

&nbsp;               error\_code=type(exc).\_\_name\_\_,

&nbsp;               human\_guidance="Idle/ghost-resource confidence will be reduced.",

&nbsp;               can\_continue\_without\_this=True,

&nbsp;               collection\_impact="No enhanced activity-based signals.",

&nbsp;           )

```



---



\## `services/api/app/services/preflight\_service.py` update



Replace `\_run\_probes()` with this shape:



```python

from services.collector.app.probes.auth\_probe import AuthProbe

from services.collector.app.probes.resource\_graph\_probe import ResourceGraphProbe

from services.collector.app.probes.reader\_probe import ReaderProbe

from services.collector.app.probes.cost\_probe import CostProbe

from services.collector.app.probes.advisor\_probe import AdvisorProbe

from services.collector.app.probes.policy\_probe import PolicyProbe

from services.collector.app.probes.activity\_probe import ActivityProbe



\# inside PreflightService.\_\_init\_\_

self.auth\_probe = AuthProbe()

self.resource\_graph\_probe = ResourceGraphProbe()

self.reader\_probe = ReaderProbe()

self.cost\_probe = CostProbe()

self.advisor\_probe = AdvisorProbe()

self.policy\_probe = PolicyProbe()

self.activity\_probe = ActivityProbe()



\# replace \_run\_probes

async def \_run\_probes(self, req: PreflightRequest) -> list\[ProbeResult]:

&nbsp;   probes: list\[ProbeResult] = \[]



&nbsp;   auth\_result, token = await self.auth\_probe.run(

&nbsp;       mode=req.mode,

&nbsp;       tenant\_id=req.tenantId,

&nbsp;       user\_assertion=None,  # wire real incoming bearer token here

&nbsp;   )

&nbsp;   probes.append(auth\_result)

&nbsp;   if not token:

&nbsp;       return probes



&nbsp;   probes.append(await self.resource\_graph\_probe.run(token, req.subscriptionId))

&nbsp;   probes.append(await self.reader\_probe.run(token, req.subscriptionId))

&nbsp;   probes.append(await self.cost\_probe.run(token, req.subscriptionId))

&nbsp;   probes.append(await self.advisor\_probe.run(token, req.subscriptionId))

&nbsp;   probes.append(await self.policy\_probe.run(token, req.subscriptionId))

&nbsp;   probes.append(await self.activity\_probe.run(token, req.subscriptionId))



&nbsp;   return probes

```



---



\## What this gives you next



This starter pack gives you:



\* \*\*real Cosmos repository shape\*\*

\* \*\*real Azure ARM / Resource Graph / Cost / Advisor / Policy / Activity probe skeletons\*\*

\* clean separation between:



&nbsp; \* API service

&nbsp; \* Azure probes

&nbsp; \* collector jobs

&nbsp; \* Cosmos persistence



That lines up with your documented ACA flow: five RBAC pre-flight probes, collector Container App Job, 91-day daily cost extraction, Advisor/policy/network signals, and strict `subscriptionId` partition isolation.



It also stays consistent with your product principle that ACA is \*\*read-only\*\* and clients deploy scripts themselves.



The clean next move is the \*\*real collection clients\*\*:



\* Resource Graph pagination

\* Cost Management pagination + 429 retry

\* Advisor normalization

\* actual scan/job trigger wiring



If you want, I’ll do that next as \*\*Phase 3 code: real collector pagination and normalization pack\*\*.




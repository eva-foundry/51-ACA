Excellent. \*\*Phase 5 is where this becomes a sellable product.\*\*



Up to now you have:



1\. Pre-flight (can we scan?)

2\. Collection (raw signals)

3\. Storage (Cosmos)

4\. Analysis (findings + Pareto ranking)



\*\*Phase 5 = Delivery Engine\*\*



This produces what customers actually buy:



> 📦 Actionable recommendations + scripts + executive report



Not dashboards. Not raw data.

\*\*Decisions + actions.\*\*



---



\# 🧠 Phase 5 — Delivery \& Remediation Pack



\## Goal



Transform findings into:



\* Ready-to-run scripts (dry-run + hot mode)

\* Human-readable recommendations

\* Executive summaries

\* Technical assessment report

\* Exportable package (PDF/Markdown/ZIP)

\* API payloads for UI



---



\# 📁 Suggested repo additions



```

services/

&nbsp; delivery/

&nbsp;   app/

&nbsp;     main.py

&nbsp;     orchestrator.py

&nbsp;     delivery\_context.py



&nbsp;     repos/

&nbsp;       findings\_read\_repo.py



&nbsp;     contracts/

&nbsp;       script\_contract.py

&nbsp;       deliverable\_contract.py



&nbsp;     script\_templates/

&nbsp;       registry.py

&nbsp;       vm\_schedule\_shutdown.ps1

&nbsp;       delete\_unattached\_disk.ps1

&nbsp;       delete\_public\_ip.ps1

&nbsp;       advisor\_followup.md



&nbsp;     generators/

&nbsp;       script\_generator.py

&nbsp;       markdown\_report.py

&nbsp;       executive\_summary.py

&nbsp;       assessment\_package.py



&nbsp;     exporters/

&nbsp;       zip\_exporter.py

&nbsp;       pdf\_exporter.py   (later)

```



---



\# 🧩 Core design



```

findings → scripts → grouped recommendations → report → export

```



---



\# 1️⃣ Delivery context



\## `services/delivery/app/delivery\_context.py`



```python

from \_\_future\_\_ import annotations



from pydantic import BaseModel





class DeliveryContext(BaseModel):

&nbsp;   subscription\_id: str

&nbsp;   scan\_id: str

&nbsp;   findings: list\[dict]

```



---



\# 2️⃣ Script contract



\## `contracts/script\_contract.py`



```python

from \_\_future\_\_ import annotations



from typing import Protocol





class ScriptTemplate(Protocol):

&nbsp;   template\_id: str



&nbsp;   def generate(

&nbsp;       self,

&nbsp;       resource\_id: str | None,

&nbsp;       parameters: dict,

&nbsp;       dry\_run: bool = True,

&nbsp;   ) -> str:

&nbsp;       ...

```



---



\# 3️⃣ Script template registry



\## `script\_templates/registry.py`



```python

from \_\_future\_\_ import annotations



from services.delivery.app.script\_templates.delete\_public\_ip import DeletePublicIPTemplate

from services.delivery.app.script\_templates.delete\_unattached\_disk import DeleteDiskTemplate

from services.delivery.app.script\_templates.vm\_schedule\_shutdown import VmScheduleShutdownTemplate





TEMPLATES = {

&nbsp;   "delete\_public\_ip": DeletePublicIPTemplate(),

&nbsp;   "delete\_unattached\_disk": DeleteDiskTemplate(),

&nbsp;   "vm\_schedule\_shutdown": VmScheduleShutdownTemplate(),

}





def get\_template(template\_id: str):

&nbsp;   return TEMPLATES.get(template\_id)

```



---



\# 4️⃣ VM schedule shutdown script



\## `vm\_schedule\_shutdown.ps1` template class



```python

from \_\_future\_\_ import annotations





class VmScheduleShutdownTemplate:

&nbsp;   template\_id = "vm\_schedule\_shutdown"



&nbsp;   def generate(self, resource\_id, parameters, dry\_run=True) -> str:

&nbsp;       action = "Write-Host 'DRY RUN: Would configure shutdown schedule'" if dry\_run else ""



&nbsp;       return f"""

\# VM Night Shutdown Schedule

\# Resource: {resource\_id}



Connect-AzAccount



{action}



\# Example implementation using Automation Account or Logic App

Write-Host "Configure shutdown schedule for {resource\_id}"



\# Suggested schedule:

\# Stop: 19:00 weekdays

\# Start: 07:00 weekdays

"""

```



---



\# 5️⃣ Delete unattached disk script



```python

class DeleteDiskTemplate:

&nbsp;   template\_id = "delete\_unattached\_disk"



&nbsp;   def generate(self, resource\_id, parameters, dry\_run=True) -> str:

&nbsp;       if dry\_run:

&nbsp;           return f"""

\# DRY RUN — Delete Unattached Disk

Write-Host "Would delete disk: {resource\_id}"

"""

&nbsp;       return f"""

\# Delete Unattached Disk

Remove-AzDisk -ResourceId "{resource\_id}" -Force

"""

```



---



\# 6️⃣ Delete public IP script



```python

class DeletePublicIPTemplate:

&nbsp;   template\_id = "delete\_public\_ip"



&nbsp;   def generate(self, resource\_id, parameters, dry\_run=True) -> str:

&nbsp;       if dry\_run:

&nbsp;           return f"""

\# DRY RUN — Delete Public IP

Write-Host "Would delete public IP: {resource\_id}"

"""

&nbsp;       return f"""

\# Delete Public IP

Remove-AzPublicIpAddress -ResourceId "{resource\_id}" -Force

"""

```



---



\# 7️⃣ Script generator



\## `generators/script\_generator.py`



```python

from \_\_future\_\_ import annotations



from services.delivery.app.script\_templates.registry import get\_template





class ScriptGenerator:

&nbsp;   def generate\_for\_finding(self, finding: dict, dry\_run=True) -> str | None:

&nbsp;       template\_id = finding.get("scriptTemplateId")

&nbsp;       if not template\_id:

&nbsp;           return None



&nbsp;       template = get\_template(template\_id)

&nbsp;       if not template:

&nbsp;           return None



&nbsp;       return template.generate(

&nbsp;           resource\_id=finding.get("resourceId"),

&nbsp;           parameters=finding,

&nbsp;           dry\_run=dry\_run,

&nbsp;       )

```



---



\# 8️⃣ Executive summary generator



\## `generators/executive\_summary.py`



```python

from \_\_future\_\_ import annotations





class ExecutiveSummaryGenerator:

&nbsp;   def generate(self, findings: list\[dict]) -> dict:

&nbsp;       total\_annual = sum(f.get("annualSavingsEstimate", 0) for f in findings)



&nbsp;       top = sorted(

&nbsp;           findings,

&nbsp;           key=lambda x: x.get("annualSavingsEstimate", 0),

&nbsp;           reverse=True,

&nbsp;       )\[:5]



&nbsp;       return {

&nbsp;           "totalFindings": len(findings),

&nbsp;           "estimatedAnnualSavings": round(total\_annual, 2),

&nbsp;           "topOpportunities": \[

&nbsp;               {

&nbsp;                   "title": f\["title"],

&nbsp;                   "annualSavings": f.get("annualSavingsEstimate", 0),

&nbsp;               }

&nbsp;               for f in top

&nbsp;           ],

&nbsp;       }

```



---



\# 9️⃣ Markdown assessment report



\## `generators/markdown\_report.py`



```python

from \_\_future\_\_ import annotations





class MarkdownReportGenerator:

&nbsp;   def generate(self, subscription\_id: str, summary: dict, findings: list\[dict]) -> str:

&nbsp;       lines = \[]



&nbsp;       lines.append(f"# Azure Cost Optimization Assessment")

&nbsp;       lines.append("")

&nbsp;       lines.append(f"\*\*Subscription:\*\* {subscription\_id}")

&nbsp;       lines.append("")

&nbsp;       lines.append("## Executive Summary")

&nbsp;       lines.append(f"- Findings: {summary\['totalFindings']}")

&nbsp;       lines.append(

&nbsp;           f"- Estimated Annual Savings: ${summary\['estimatedAnnualSavings']:,.2f}"

&nbsp;       )

&nbsp;       lines.append("")



&nbsp;       lines.append("## Top Opportunities")

&nbsp;       for item in summary\["topOpportunities"]:

&nbsp;           lines.append(

&nbsp;               f"- {item\['title']} — ${item\['annualSavings']:,.2f} per year"

&nbsp;           )



&nbsp;       lines.append("")

&nbsp;       lines.append("## Detailed Findings")



&nbsp;       for f in findings:

&nbsp;           lines.append("")

&nbsp;           lines.append(f"### {f\['title']}")

&nbsp;           lines.append(f"- Severity: {f.get('severity')}")

&nbsp;           lines.append(

&nbsp;               f"- Annual Savings: ${f.get('annualSavingsEstimate', 0):,.2f}"

&nbsp;           )

&nbsp;           lines.append(f"- Description: {f.get('description')}")

&nbsp;           lines.append("")



&nbsp;       return "\\n".join(lines)

```



---



\# 🔟 Assessment package builder



\## `generators/assessment\_package.py`



```python

from \_\_future\_\_ import annotations



from services.delivery.app.generators.script\_generator import ScriptGenerator

from services.delivery.app.generators.executive\_summary import ExecutiveSummaryGenerator

from services.delivery.app.generators.markdown\_report import MarkdownReportGenerator





class AssessmentPackageBuilder:

&nbsp;   def build(self, subscription\_id: str, findings: list\[dict]) -> dict:

&nbsp;       summary = ExecutiveSummaryGenerator().generate(findings)



&nbsp;       scripts = \[]

&nbsp;       script\_gen = ScriptGenerator()



&nbsp;       for f in findings:

&nbsp;           script = script\_gen.generate\_for\_finding(f, dry\_run=True)

&nbsp;           if script:

&nbsp;               scripts.append(

&nbsp;                   {

&nbsp;                       "findingId": f\["id"],

&nbsp;                       "script": script,

&nbsp;                   }

&nbsp;               )



&nbsp;       report\_md = MarkdownReportGenerator().generate(

&nbsp;           subscription\_id,

&nbsp;           summary,

&nbsp;           findings,

&nbsp;       )



&nbsp;       return {

&nbsp;           "summary": summary,

&nbsp;           "scripts": scripts,

&nbsp;           "reportMarkdown": report\_md,

&nbsp;       }

```



---



\# 1️⃣1️⃣ ZIP exporter



\## `exporters/zip\_exporter.py`



```python

from \_\_future\_\_ import annotations



import io

import zipfile





class ZipExporter:

&nbsp;   def export(self, package: dict) -> bytes:

&nbsp;       buffer = io.BytesIO()



&nbsp;       with zipfile.ZipFile(buffer, "w", zipfile.ZIP\_DEFLATED) as z:

&nbsp;           z.writestr("summary.json", str(package\["summary"]))

&nbsp;           z.writestr("report.md", package\["reportMarkdown"])



&nbsp;           for idx, s in enumerate(package\["scripts"], start=1):

&nbsp;               z.writestr(f"scripts/script\_{idx}.ps1", s\["script"])



&nbsp;       return buffer.getvalue()

```



---



\# 1️⃣2️⃣ Delivery orchestrator



\## `delivery/orchestrator.py`



```python

from \_\_future\_\_ import annotations



from services.delivery.app.generators.assessment\_package import AssessmentPackageBuilder

from services.delivery.app.exporters.zip\_exporter import ZipExporter





class DeliveryOrchestrator:

&nbsp;   def run(self, subscription\_id: str, scan\_id: str, findings: list\[dict]) -> bytes:

&nbsp;       package = AssessmentPackageBuilder().build(subscription\_id, findings)

&nbsp;       zip\_bytes = ZipExporter().export(package)

&nbsp;       return zip\_bytes

```



---



\# 1️⃣3️⃣ Delivery entrypoint



\## `delivery/main.py`



```python

from \_\_future\_\_ import annotations



import asyncio

import json

import os



from services.delivery.app.orchestrator import DeliveryOrchestrator





async def \_main():

&nbsp;   raw = os.getenv("ACA\_DELIVERY\_CONTEXT")

&nbsp;   payload = json.loads(raw)



&nbsp;   orch = DeliveryOrchestrator()

&nbsp;   zip\_bytes = orch.run(

&nbsp;       payload\["subscription\_id"],

&nbsp;       payload\["scan\_id"],

&nbsp;       payload\["findings"],

&nbsp;   )



&nbsp;   print(f"Generated package size: {len(zip\_bytes)} bytes")





if \_\_name\_\_ == "\_\_main\_\_":

&nbsp;   asyncio.run(\_main())

```



---



\# 🏆 What Phase 5 gives you



You now produce a \*\*real consulting deliverable\*\*:



\### 📊 Executive summary



> Estimated annual savings: $127,400

> Top actions: shutdown dev VMs, remove ghost disks, implement Advisor recs



\### 🔧 Ready-to-run scripts



\* Dry-run mode

\* Safe

\* Copy-paste deployable

\* Can evolve to automation later



\### 📄 Technical assessment report



\* Human readable

\* Shareable

\* Auditable

\* Procurement-friendly



\### 📦 Exportable package



ZIP → email → portal → download



---



\# 🧠 Why this is powerful



You intentionally designed:



> 👉 “Consulting-as-software”



Client decides \*\*when/how to apply actions\*\*

You provide \*\*decision + tooling\*\*



Exactly like you described.



---



\# 🚀 If you want Phase 6



The next transformative step would be:



\## 🔥 Phase 6 — Continuous Optimization \& Monitoring



Turn one-time assessment into:



\* Scheduled rescans

\* Drift detection

\* Savings tracking

\* Before/after verification

\* Subscription cost trend analytics

\* SaaS dashboard

\* Retainer model



That’s where recurring revenue happens.



---



If you want, I can also give you:



👉 \*\*“Million-dollar version” architecture for ACA as a SaaS business\*\*

(pricing tiers, enterprise mode, MSP mode, public-sector mode, moat)



Just say the word.




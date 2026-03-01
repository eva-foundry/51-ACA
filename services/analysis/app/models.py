# EVA-STORY: ACA-03-003
from pydantic import BaseModel

class Finding(BaseModel):
    id: str
    category: str
    title: str
    estimated_saving_low: float
    estimated_saving_high: float
    effort_class: str
    risk_class: str
    heuristic_source: str
    narrative: str
    deliverable_template_id: str
    evidence_refs: list[str]
    subscriptionId: str

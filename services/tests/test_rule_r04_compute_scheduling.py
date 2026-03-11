# EVA-STORY: ACA-03-014
from services.analysis.app.rules.r04_compute_scheduling import evaluate_r04_compute_scheduling


def test_evaluate_r04_compute_scheduling():
    subscription_id = "test-subscription"
    client_tier = 1
    findings = evaluate_r04_compute_scheduling(
        subscription_id,
        client_tier,
        compute_cost_data=[
            {"serviceName": "Virtual Machines", "totalAnnualCost": 3000},
            {"serviceName": "App Service", "totalAnnualCost": 2500},
        ],
    )

    assert len(findings) == 1
    assert findings[0]["id"] == f"r04-{subscription_id}"
    assert findings[0]["category"] == "compute-cost-optimization"
    assert findings[0]["title"] == "Annual schedulable compute cost exceeds $5,000"
    assert findings[0]["estimated_saving_low"] == 500
    assert findings[0]["estimated_saving_high"] == 1500
    assert findings[0]["effort_class"] == "medium"
    assert findings[0]["risk_class"] == "low"


def test_evaluate_r04_compute_scheduling_below_threshold():
    findings = evaluate_r04_compute_scheduling(
        "test-subscription",
        1,
        compute_cost_data=[
            {"serviceName": "Virtual Machines", "totalAnnualCost": 3000},
            {"serviceName": "App Service", "totalAnnualCost": 1000},
        ],
    )
    assert findings == []


def test_evaluate_r04_compute_scheduling_output_fields():
    findings = evaluate_r04_compute_scheduling(
        "test-subscription",
        2,
        compute_cost_data=[
            {"serviceName": "Virtual Machines", "totalAnnualCost": 6000},
        ],
    )
    assert set(findings[0].keys()) == {
        "id",
        "subscriptionId",
        "category",
        "title",
        "estimated_saving_low",
        "estimated_saving_high",
        "effort_class",
        "risk_class",
    }
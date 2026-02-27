"""
Azure collector -- wraps Azure SDK calls for resource/cost/advisor/network/policy.
"""
import os
from datetime import datetime, timedelta, timezone

from azure.identity import ClientSecretCredential
from azure.mgmt.resource import ResourceManagementClient
from azure.mgmt.costmanagement import CostManagementClient
from azure.mgmt.advisor import AdvisorManagementClient
from azure.mgmt.network import NetworkManagementClient
from azure.mgmt.policyinsights import PolicyInsightsClient


def _credential():
    return ClientSecretCredential(
        tenant_id=os.environ["AZURE_TENANT_ID"],
        client_id=os.environ["AZURE_CLIENT_ID"],
        client_secret=os.environ["AZURE_CLIENT_SECRET"],
    )


class AzureCollector:
    def __init__(self, subscription_id: str):
        self.sub_id = subscription_id
        self.cred = _credential()

    def get_inventory(self) -> list[dict]:
        """List all resources in the subscription via ResourceManagementClient."""
        client = ResourceManagementClient(self.cred, self.sub_id)
        resources = []
        for r in client.resources.list():
            resources.append({
                "id": r.id,
                "name": r.name,
                "type": r.type,
                "location": r.location,
                "resource_group": r.id.split("/")[4] if r.id else "",
                "tags": r.tags or {},
                "sku": r.sku.name if r.sku else None,
            })
        return resources

    def get_cost_data(self, days: int = 91) -> list[dict]:
        """
        Pull daily cost data for the last N days via Cost Management Query API.
        Returns list of {date, meter_category, resource_group, cost_usd}
        """
        client = CostManagementClient(self.cred)
        scope = f"/subscriptions/{self.sub_id}"
        end = datetime.now(timezone.utc)
        start = end - timedelta(days=days)

        from azure.mgmt.costmanagement.models import (
            QueryDefinition, QueryTimePeriod, QueryDataset,
            QueryGrouping, QueryAggregation, TimeframeType,
        )

        query = QueryDefinition(
            type="Usage",
            timeframe=TimeframeType.CUSTOM,
            time_period=QueryTimePeriod(
                from_property=start,
                to=end,
            ),
            dataset=QueryDataset(
                granularity="Daily",
                aggregation={"totalCost": QueryAggregation(name="Cost", function="Sum")},
                grouping=[
                    QueryGrouping(type="Dimension", name="MeterCategory"),
                    QueryGrouping(type="Dimension", name="ResourceGroup"),
                ],
            ),
        )
        result = client.query.usage(scope=scope, parameters=query)
        rows = []
        if result and result.rows:
            cols = [c.name for c in result.columns]
            for row in result.rows:
                rows.append(dict(zip(cols, row)))
        return rows

    def get_advisor_recommendations(self) -> list[dict]:
        """Retrieve all Advisor recommendations (all 5 categories)."""
        client = AdvisorManagementClient(self.cred, self.sub_id)
        recs = []
        for r in client.recommendations.list():
            recs.append({
                "id": r.id,
                "name": r.name,
                "category": r.category,
                "impact": r.impact,
                "resource_id": r.resource_metadata.resource_id if r.resource_metadata else None,
                "short_description": r.short_description.problem if r.short_description else "",
                "solution": r.short_description.solution if r.short_description else "",
                "potential_benefits": r.potential_benefits,
                "last_updated": str(r.last_updated) if r.last_updated else None,
            })
        return recs

    def get_policy_state(self) -> dict:
        """Get policy state summary for the subscription."""
        client = PolicyInsightsClient(self.cred)
        results = list(client.policy_states.list_query_results_for_subscription(
            policy_states_resource="latest",
            subscription_id=self.sub_id,
        ))
        noncompliant = [r for r in results if r.compliance_state == "NonCompliant"]
        return {
            "total": len(results),
            "noncompliant": len(noncompliant),
            "details": [
                {
                    "resource_id": r.resource_id,
                    "policy_definition_name": r.policy_definition_name,
                    "compliance_state": r.compliance_state,
                }
                for r in noncompliant[:100]  # cap at 100 for storage
            ],
        }

    def get_network_topology(self) -> dict:
        """Pull NSG rules, public IPs, private DNS zones, VNet peering count."""
        client = NetworkManagementClient(self.cred, self.sub_id)
        public_ips = [
            {"name": ip.name, "ip": ip.ip_address, "rg": ip.id.split("/")[4]}
            for ip in client.public_ip_addresses.list_all()
            if ip.ip_address
        ]
        nsg_count = sum(1 for _ in client.network_security_groups.list_all())
        vnet_count = sum(1 for _ in client.virtual_networks.list_all())
        return {
            "public_ip_count": len(public_ips),
            "public_ips": public_ips[:50],  # cap for storage
            "nsg_count": nsg_count,
            "vnet_count": vnet_count,
        }

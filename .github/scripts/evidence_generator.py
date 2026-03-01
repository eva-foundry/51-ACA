#!/usr/bin/env python3
# EVA-STORY: ACA-14-004
# evidence_generator.py -- Generate and validate evidence receipts for DPDCA stories
#
# Integrated with:
# - SprintContext (correlation_id, timeline, cost tracking)
# - state_lock (idempotency proof)
# - phase_verifier (quality gate results)
# - Evidence catalog (7 evidence types)
#
# Usage:
#   ctx = SprintContext("ACA-S11-...")
#   gen = EvidenceGenerator(ctx, story_id="ACA-14-001")
#   gen.add_universal_data(phase="A", lint="PASS", test="PASS")
#   gen.add_infrastructure_data(containers_running=4, health_check="ok")
#   receipt = gen.generate()
#   gen.persist(".eva/evidence/")

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional, List


class EvidenceMetadata:
    """Base metadata for all evidence types."""
    
    def __init__(self, story_id: str, story_type: str, phase: str):
        self.story_id = story_id
        self.story_type = story_type  # infrastructure, ci_pipeline, api_endpoint, etc
        self.phase = phase  # D1, D2, P, D3, A
        self.timestamp = datetime.now(timezone.utc).isoformat() + "Z"
        self.universal_fields = {}
        self.type_fields = {}
    
    def add_universal(self, **kwargs):
        """Add universal fields: test_result, lint_result, duration_ms, artifacts, etc."""
        for key, value in kwargs.items():
            self.universal_fields[key] = value
    
    def add_type_specific(self, **kwargs):
        """Add type-specific fields based on story type."""
        for key, value in kwargs.items():
            self.type_fields[key] = value
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to evidence dictionary."""
        evidence = {
            "story_id": self.story_id,
            "type": self.story_type,
            "phase": self.phase,
            "timestamp": self.timestamp,
        }
        evidence.update(self.universal_fields)
        evidence.update(self.type_fields)
        return evidence


class EvidenceGenerator:
    """Generates evidence receipts for stories in the DPDCA cycle."""
    
    def __init__(self, story_id: str, story_type: str, phase: str = "A", 
                 correlation_id: Optional[str] = None):
        """
        Initialize evidence generator.
        
        Args:
            story_id: "ACA-NN-NNN" format
            story_type: One of [infrastructure, ci_pipeline, api_endpoint, 
                               data_collection, business_logic, frontend, e2e_workflow]
            phase: DPDCA phase ("D1", "D2", "P", "D3", "A")
            correlation_id: From SprintContext (optional, can be added later)
        """
        self.metadata = EvidenceMetadata(story_id, story_type, phase)
        self.correlation_id = correlation_id
        self.lm_cost = 0.0
        self.lm_tokens = 0
    
    def add_universal_data(self, 
                          title: Optional[str] = None,
                          artifacts: Optional[List[str]] = None,
                          test_result: str = "PASS",
                          lint_result: str = "PASS",
                          duration_ms: int = 0,
                          commit_sha: Optional[str] = None,
                          tokens_used: int = 0,
                          test_count_before: int = 0,
                          test_count_after: int = 0,
                          files_changed: int = 0):
        """Add universal fields present in all evidence types."""
        universal = {}
        if title:
            universal["title"] = title
        if artifacts:
            universal["artifacts"] = artifacts
        universal["test_result"] = test_result
        universal["lint_result"] = lint_result
        universal["duration_ms"] = duration_ms
        if commit_sha:
            universal["commit_sha"] = commit_sha
        universal["tokens_used"] = tokens_used
        universal["test_count_before"] = test_count_before
        universal["test_count_after"] = test_count_after
        universal["files_changed"] = files_changed
        
        if self.correlation_id:
            universal["correlation_id"] = self.correlation_id
        
        self.metadata.add_universal(**universal)
    
    def add_infrastructure_data(self,
                               outcome: Optional[str] = None,
                               validation_method: Optional[str] = None,
                               logs: Optional[str] = None,
                               success_criteria: Optional[str] = None,
                               containers_running: Optional[int] = None,
                               service_health: Optional[Dict[str, str]] = None):
        """Add infrastructure-specific fields."""
        infrastructure = {}
        if outcome:
            infrastructure["outcome"] = outcome
        if validation_method:
            infrastructure["validation_method"] = validation_method
        if logs:
            infrastructure["logs"] = logs
        if success_criteria:
            infrastructure["success_criteria"] = success_criteria
        if containers_running is not None:
            infrastructure["containers_running"] = containers_running
        if service_health:
            infrastructure["service_health"] = service_health
        
        self.metadata.add_type_specific(**infrastructure)
    
    def add_ci_pipeline_data(self,
                            workflow_file: Optional[str] = None,
                            test_command: Optional[str] = None,
                            files_checked: int = 0,
                            issues_found: int = 0):
        """Add CI/CD pipeline-specific fields."""
        pipeline = {}
        if workflow_file:
            pipeline["workflow_file"] = workflow_file
        if test_command:
            pipeline["test_command"] = test_command
        pipeline["files_checked"] = files_checked
        pipeline["issues_found"] = issues_found
        
        self.metadata.add_type_specific(**pipeline)
    
    def add_api_endpoint_data(self,
                             endpoint: Optional[str] = None,
                             request_schema: Optional[Dict] = None,
                             response_schema: Optional[Dict] = None,
                             status_code: int = 200,
                             response_time_ms: int = 0,
                             test_queries: int = 0,
                             validation_passed: int = 0):
        """Add API endpoint-specific fields."""
        api = {}
        if endpoint:
            api["endpoint"] = endpoint
        if request_schema:
            api["request_schema"] = request_schema
        if response_schema:
            api["response_schema"] = response_schema
        api["status_code"] = status_code
        api["response_time_ms"] = response_time_ms
        api["test_queries"] = test_queries
        api["validation_passed"] = validation_passed
        
        self.metadata.add_type_specific(**api)
    
    def add_data_collection_data(self,
                                data_source: Optional[str] = None,
                                resource_count: int = 0,
                                cosmos_writes: int = 0,
                                cosmos_container: Optional[str] = None,
                                partition_key: Optional[str] = None,
                                validation: Optional[str] = None):
        """Add data collection-specific fields."""
        collection = {}
        if data_source:
            collection["data_source"] = data_source
        collection["resource_count"] = resource_count
        collection["cosmos_writes"] = cosmos_writes
        if cosmos_container:
            collection["cosmos_container"] = cosmos_container
        if partition_key:
            collection["partition_key"] = partition_key
        if validation:
            collection["validation"] = validation
        
        self.metadata.add_type_specific(**collection)
    
    def add_business_logic_data(self,
                               description: Optional[str] = None,
                               test_cases: int = 0,
                               test_passed: int = 0,
                               test_coverage: float = 0.0,
                               example_input: Optional[Dict] = None,
                               example_output: Optional[Dict] = None):
        """Add business logic / rule-specific fields."""
        logic = {}
        if description:
            logic["description"] = description
        logic["test_cases"] = test_cases
        logic["test_passed"] = test_passed
        logic["test_coverage"] = test_coverage
        if example_input:
            logic["example_input"] = example_input
        if example_output:
            logic["example_output"] = example_output
        
        self.metadata.add_type_specific(**logic)
    
    def add_frontend_data(self,
                         component_path: Optional[str] = None,
                         test_file: Optional[str] = None,
                         test_count: int = 0,
                         test_passed: int = 0,
                         coverage: Optional[Dict[str, float]] = None,
                         a11y_violations: int = 0,
                         a11y_warnings: int = 0):
        """Add frontend/UI-specific fields."""
        frontend = {}
        if component_path:
            frontend["component_path"] = component_path
        if test_file:
            frontend["test_file"] = test_file
        frontend["test_count"] = test_count
        frontend["test_passed"] = test_passed
        if coverage:
            frontend["coverage"] = coverage
        frontend["a11y_violations"] = a11y_violations
        frontend["a11y_warnings"] = a11y_warnings
        
        self.metadata.add_type_specific(**frontend)
    
    def add_e2e_workflow_data(self,
                             outcome: Optional[str] = None,
                             workflow_steps: Optional[List[Dict]] = None,
                             total_duration_ms: int = 0,
                             resources_collected: int = 0,
                             findings_produced: int = 0):
        """Add E2E workflow-specific fields."""
        e2e = {}
        if outcome:
            e2e["outcome"] = outcome
        if workflow_steps:
            e2e["workflow_steps"] = workflow_steps
        e2e["total_duration_ms"] = total_duration_ms
        e2e["resources_collected"] = resources_collected
        e2e["findings_produced"] = findings_produced
        
        self.metadata.add_type_specific(**e2e)
    
    def generate(self) -> Dict[str, Any]:
        """Generate and return evidence dictionary."""
        return self.metadata.to_dict()
    
    def validate(self) -> tuple[bool, str]:
        """
        Validate evidence against schema.
        
        Returns:
            (is_valid: bool, error_msg: str or "OK")
        """
        evidence = self.metadata.to_dict()
        
        # Universal required fields
        required_universal = ["story_id", "type", "phase", "timestamp", "test_result", "lint_result"]
        for field in required_universal:
            if field not in evidence:
                return False, f"Missing required field: {field}"
        
        # Type-specific required fields
        type_requirements = {
            "infrastructure": ["outcome"],
            "ci_pipeline": ["workflow_file", "test_command"],
            "api_endpoint": ["endpoint", "status_code"],
            "data_collection": ["data_source", "resource_count"],
            "business_logic": ["test_cases", "test_coverage"],
            "frontend": ["component_path", "test_count"],
            "e2e_workflow": ["workflow_steps", "total_duration_ms"]
        }
        
        story_type = evidence.get("type")
        if story_type in type_requirements:
            required = type_requirements[story_type]
            for field in required:
                if field not in evidence or evidence[field] is None:
                    return False, f"Missing required field for {story_type}: {field}"
        
        # Test/lint result validation
        test_result = evidence.get("test_result", "")
        if test_result not in ["PASS", "FAIL", "WARN"]:
            return False, f"Invalid test_result: {test_result}"
        
        lint_result = evidence.get("lint_result", "")
        if lint_result not in ["PASS", "FAIL", "WARN"]:
            return False, f"Invalid lint_result: {lint_result}"
        
        # Test result FAIL blocks (cannot merge)
        if test_result == "FAIL":
            return False, "Story tests FAILED -- cannot merge"
        if lint_result == "FAIL":
            return False, "Story linting FAILED -- cannot merge"
        
        return True, "OK"
    
    def persist(self, evidence_dir: str = ".eva/evidence") -> str:
        """
        Persist evidence to JSON file.
        
        Args:
            evidence_dir: Directory to write evidence files
        
        Returns:
            Path to written file
        """
        evidence_path = Path(evidence_dir)
        evidence_path.mkdir(parents=True, exist_ok=True)
        
        # Validate before persisting
        is_valid, msg = self.validate()
        if not is_valid:
            raise ValueError(f"Evidence validation failed: {msg}")
        
        # Generate filename from story_id
        story_id = self.metadata.story_id
        filename = f"{story_id}-receipt.json"
        filepath = evidence_path / filename
        
        # Write evidence
        evidence = self.generate()
        with open(filepath, "w") as f:
            json.dump(evidence, f, indent=2)
        
        print(f"[INFO] Evidence persisted: {filepath}")
        return str(filepath)


if __name__ == "__main__":
    # Example usage: Generate mock evidence for ACA-14-001
    print("Testing EvidenceGenerator...\n")
    
    # Example 1: Infrastructure story
    gen = EvidenceGenerator(
        story_id="ACA-14-001",
        story_type="infrastructure",
        phase="A",
        correlation_id="ACA-S11-20260301-a1b2c3d4"
    )
    gen.add_universal_data(
        title="Sprint context initialized and tested",
        artifacts=[".github/scripts/sprint_context.py", ".github/scripts/aca_lm_tracer.py"],
        test_result="PASS",
        lint_result="PASS",
        duration_ms=15000,
        commit_sha="abc123def456",
        tokens_used=7202,
        files_changed=2
    )
    gen.add_infrastructure_data(
        outcome="SprintContext class created with unified tracing",
        validation_method="pytest .github/scripts/sprint_context.py",
        success_criteria="All 5 acceptance criteria pass",
        service_health={"context": "initialized", "tracer": "active"}
    )
    
    is_valid, msg = gen.validate()
    print(f"[TEST] Validation: {msg}" if is_valid else f"[FAIL] {msg}")
    
    evidence = gen.generate()
    print(f"\n[TEST] Generated evidence:")
    print(json.dumps(evidence, indent=2))
    
    # Example 2: Business logic story
    print("\n\n=== Example 2: Business Logic Story ===\n")
    gen2 = EvidenceGenerator(
        story_id="ACA-03-019",
        story_type="business_logic",
        phase="A",
        correlation_id="ACA-S09-20260301-x1y2z3w4"
    )
    gen2.add_universal_data(
        title="Rule R-09: DNS Sprawl detection",
        artifacts=["services/analysis/rules/r09_dns_sprawl.py"],
        test_result="PASS",
        lint_result="PASS",
        duration_ms=8234,
        test_count_after=4,
        files_changed=1
    )
    gen2.add_business_logic_data(
        description="Detects DNS zones with annual cost > $1,000",
        test_cases=7,
        test_passed=7,
        test_coverage=92.5,
        example_output={"findings": [{"category": "Network", "title": "DNS Sprawl", "estimated_saving": 1234}]}
    )
    
    is_valid2, msg2 = gen2.validate()
    print(f"[TEST] Validation: {msg2}" if is_valid2 else f"[FAIL] {msg2}")
    
    evidence2 = gen2.generate()
    print(f"\n[TEST] Generated evidence:")
    print(json.dumps(evidence2, indent=2))
    
    print("\n[PASS] EvidenceGenerator operational")

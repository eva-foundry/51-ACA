# EVA-STORY: ACA-14-010
"""
Evidence receipt schema validation.

Validates that evidence receipts conform to required schema before writing.
Ensures Veritas audit can parse all receipt files without error.
"""
import json
from typing import Any, Dict

# Required fields for Veritas evidence receipts
REQUIRED_FIELDS = [
    "story_id",
    "phase",
    "timestamp",
    "test_result",
    "duration_ms",
    "tokens_used",
    "test_count_before",
    "test_count_after",
    "files_changed",
]

# Optional but recommended fields
OPTIONAL_FIELDS = [
    "title",
    "artifacts",
    "lint_result",
    "commit_sha",
    "correlation_id",
    "outcome",
    "validation_method",
    "success_criteria",
    "wbs_id",
    "epic",
    "branch",
    "model",
]

VALID_PHASES = ["D", "P", "D|P|D|C|A", "A", "C"]
VALID_TEST_RESULTS = ["PASS", "FAIL", "WARN", "SKIP"]


def validate_evidence_schema(receipt: Dict[str, Any]) -> tuple[bool, list[str]]:
    """
    Validate evidence receipt against required schema.
    
    Args:
        receipt: Evidence receipt dictionary
        
    Returns:
        (is_valid, errors) tuple
        - is_valid: True if schema is valid
        - errors: List of validation error messages (empty if valid)
    """
    errors = []
    
    # Check required fields
    for field in REQUIRED_FIELDS:
        if field not in receipt:
            errors.append(f"Missing required field: {field}")
        elif receipt[field] is None:
            errors.append(f"Required field cannot be None: {field}")
    
    # Type validation
    if "story_id" in receipt and not isinstance(receipt["story_id"], str):
        errors.append(f"story_id must be string, got {type(receipt['story_id']).__name__}")
    
    if "phase" in receipt and receipt["phase"] not in VALID_PHASES:
        errors.append(f"phase must be one of {VALID_PHASES}, got {receipt['phase']}")
    
    if "test_result" in receipt and receipt["test_result"] not in VALID_TEST_RESULTS:
        errors.append(f"test_result must be one of {VALID_TEST_RESULTS}, got {receipt['test_result']}")
    
    # Numeric field validation
    for field in ["duration_ms", "tokens_used", "test_count_before", "test_count_after", "files_changed"]:
        if field in receipt:
            if not isinstance(receipt[field], int):
                errors.append(f"{field} must be integer, got {type(receipt[field]).__name__}")
            elif receipt[field] < 0:
                errors.append(f"{field} cannot be negative, got {receipt[field]}")
    
    # timestamp format check (ISO 8601)
    if "timestamp" in receipt:
        timestamp = receipt["timestamp"]
        if not isinstance(timestamp, str):
            errors.append(f"timestamp must be string, got {type(timestamp).__name__}")
        elif "T" not in timestamp or "Z" not in timestamp:
            errors.append(f"timestamp must be ISO 8601 format (YYYY-MM-DDTHH:MM:SSZ), got {timestamp}")
    
    # artifacts must be list if present
    if "artifacts" in receipt and not isinstance(receipt["artifacts"], list):
        errors.append(f"artifacts must be list, got {type(receipt['artifacts']).__name__}")
    
    return (len(errors) == 0, errors)


if __name__ == "__main__":
    # Test valid receipt
    valid_receipt = {
        "story_id": "ACA-14-010",
        "phase": "A",
        "timestamp": "2026-03-01T20:30:00Z",
        "test_result": "PASS",
        "duration_ms": 5000,
        "tokens_used": 1250,
        "test_count_before": 24,
        "test_count_after": 27,
        "files_changed": 3,
        "artifacts": ["path/to/file.py"],
    }
    
    is_valid, errors = validate_evidence_schema(valid_receipt)
    print(f"[TEST] Valid receipt: {is_valid} (errors={len(errors)})")
    
    # Test invalid receipt
    invalid_receipt = {
        "story_id": "ACA-14-010",
        "phase": "INVALID",
        "timestamp": "2026-03-01 20:30:00",  # Wrong format
        "test_result": "MAYBE",  # Invalid value
        "duration_ms": -100,  # Negative
        "tokens_used": "many",  # Wrong type
    }
    
    is_valid, errors = validate_evidence_schema(invalid_receipt)
    print(f"[TEST] Invalid receipt: {is_valid} (errors={len(errors)})")
    for err in errors:
        print(f"  - {err}")

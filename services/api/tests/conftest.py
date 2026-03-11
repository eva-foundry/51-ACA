# EVA-STORY: ACA-04-001
"""Pytest configuration: inject mock env vars before app modules are imported.

Settings requires ACA_COSMOS_URL, ACA_COSMOS_KEY, ACA_OPENAI_ENDPOINT,
ACA_OPENAI_KEY, STRIPE_SECRET_KEY, STRIPE_WEBHOOK_SECRET at import time.
These mock values prevent pydantic ValidationError during test collection.
"""
import os

os.environ.setdefault("ACA_COSMOS_URL", "https://mock-cosmos.documents.azure.com:443/")
os.environ.setdefault("ACA_COSMOS_KEY", "mock-cosmos-key-for-testing-only")
os.environ.setdefault("ACA_OPENAI_ENDPOINT", "https://mock-openai.openai.azure.com/")
os.environ.setdefault("ACA_OPENAI_KEY", "mock-openai-key-for-testing-only")
os.environ.setdefault("STRIPE_SECRET_KEY", "sk_test_mock_key_for_testing_only")
os.environ.setdefault("STRIPE_WEBHOOK_SECRET", "whsec_mock_for_testing_only")

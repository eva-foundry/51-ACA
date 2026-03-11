# EVA-STORY: ACA-03-010
"""Pytest configuration: inject mock env vars and api sys.path before app modules
are imported. Settings requires 6 required fields at import time; these mock
values prevent pydantic ValidationError during test collection.
"""
import os
import sys

# Add services/api to sys.path so tests can import app.* modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "api"))

os.environ.setdefault("ACA_COSMOS_URL", "https://mock-cosmos.documents.azure.com:443/")
os.environ.setdefault("ACA_COSMOS_KEY", "mock-cosmos-key-for-testing-only")
os.environ.setdefault("ACA_OPENAI_ENDPOINT", "https://mock-openai.openai.azure.com/")
os.environ.setdefault("ACA_OPENAI_KEY", "mock-openai-key-for-testing-only")
os.environ.setdefault("STRIPE_SECRET_KEY", "sk_test_mock_key_for_testing_only")
os.environ.setdefault("STRIPE_WEBHOOK_SECRET", "whsec_mock_for_testing_only")

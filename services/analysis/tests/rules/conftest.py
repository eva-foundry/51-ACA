# EVA-STORY: ACA-03-019
"""Pytest configuration: add rules directory to sys.path for direct imports."""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "app", "rules"))

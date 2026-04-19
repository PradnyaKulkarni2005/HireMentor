#!/usr/bin/env python3
"""Quick test to verify backend imports work after spaCy startup event change."""

try:
    from main import app
    print("✅ Backend imports successfully")
    print("✅ No spaCy loading issues during import")
except Exception as e:
    print(f"❌ Import failed: {e}")
    exit(1)
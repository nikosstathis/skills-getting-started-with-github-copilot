#!/usr/bin/env python
"""
Run pytest tests programmatically
"""
import sys
import os

# Change to the project directory
os.chdir('/workspaces/skills-getting-started-with-github-copilot')

# Add src to path
sys.path.insert(0, '/workspaces/skills-getting-started-with-github-copilot/src')

# Import and run pytest
import pytest

# Run pytest with verbose output
exit_code = pytest.main([
    'tests/test_app.py',
    '-v',
    '--tb=short',
    '--color=yes'
])

print(f"\n{'='*70}")
print(f"Test run completed with exit code: {exit_code}")
print(f"{'='*70}")

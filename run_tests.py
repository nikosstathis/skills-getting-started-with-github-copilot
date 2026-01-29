#!/usr/bin/env python
"""
Simple test runner script
"""
import subprocess
import sys

result = subprocess.run(
    [sys.executable, "-m", "pytest", "tests/test_app.py", "-v", "--tb=short"],
    cwd="/workspaces/skills-getting-started-with-github-copilot"
)
sys.exit(result.returncode)

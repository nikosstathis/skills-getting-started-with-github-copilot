#!/bin/bash
cd /workspaces/skills-getting-started-with-github-copilot
python -m pytest tests/test_app.py -v --tb=short

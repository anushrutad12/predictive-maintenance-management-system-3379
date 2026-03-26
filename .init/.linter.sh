#!/bin/bash
cd /home/kavia/workspace/code-generation/predictive-maintenance-management-system-3379/predictive_maintenance_backend
source venv/bin/activate
flake8 .
LINT_EXIT_CODE=$?
if [ $LINT_EXIT_CODE -ne 0 ]; then
  exit 1
fi


"""Workflow specifications for Kei agent capabilities.

Each module defines a typed, harness-neutral workflow spec: step data models,
semantic connector references, permission requirements, and the complete
``WorkflowSpec`` constant.  No workflow engine dependency, no provider clients,
no credentials, no org/workspace arguments — routing context comes from the
governed connector bindings at execution time.
"""

from __future__ import annotations

from agents.workflows.bug_to_linear_pr import BUG_TO_LINEAR_PR

WORKFLOW_SPECS: list = [BUG_TO_LINEAR_PR]

__all__ = [
    "BUG_TO_LINEAR_PR",
    "WORKFLOW_SPECS",
]

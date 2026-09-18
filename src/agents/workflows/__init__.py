"""Workflow specifications for Kei agents.

Workflows define typed, harness-neutral step DAGs that compose governed
connector capabilities (Drive, CRM, Linear) into domain-specific processes.
Each step captures domain intent only; the harness resolves bindings,
enforces policy, and invokes provider adapters.
"""

from __future__ import annotations

from agents.workflows.finance import (
    FINANCE_WORKFLOW_SPECS,
    ApprovalGate,
    CRMLookup,
    CRMUpdate,
    DriveArchive,
    DriveRead,
    FinanceEntity,
    FinanceStepCategory,
    FinanceWorkflowSpec,
    FinanceWorkflowState,
    FinanceWorkflowStep,
    LinearTask,
    Notify,
    StepPayload,
    egress_steps,
    expense_report_workflow,
    invoice_processing_workflow,
    validate_read_first,
    vendor_onboarding_workflow,
)
from agents.workflows.github_pr_review import (
    PR_REVIEW_TOOL_DEPENDENCIES,
    PRReviewFinding,
    PRReviewFindingSeverity,
    PRReviewInput,
    PRReviewOutput,
    PRReviewStep,
    PRReviewWorkflowSpec,
    ReviewAction,
    ReviewActionKind,
)

WORKFLOW_DEFINITIONS: list[PRReviewWorkflowSpec] = [
    PRReviewWorkflowSpec(),
]

__all__ = [
    "FINANCE_WORKFLOW_SPECS",
    "PR_REVIEW_TOOL_DEPENDENCIES",
    "WORKFLOW_DEFINITIONS",
    "ApprovalGate",
    "CRMLookup",
    "CRMUpdate",
    "DriveArchive",
    "DriveRead",
    "FinanceEntity",
    "FinanceStepCategory",
    "FinanceWorkflowSpec",
    "FinanceWorkflowState",
    "FinanceWorkflowStep",
    "LinearTask",
    "Notify",
    "PRReviewFinding",
    "PRReviewFindingSeverity",
    "PRReviewInput",
    "PRReviewOutput",
    "PRReviewStep",
    "PRReviewWorkflowSpec",
    "ReviewAction",
    "ReviewActionKind",
    "StepPayload",
    "egress_steps",
    "expense_report_workflow",
    "invoice_processing_workflow",
    "validate_read_first",
    "vendor_onboarding_workflow",
]

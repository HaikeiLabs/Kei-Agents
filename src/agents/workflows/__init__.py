"""Workflow specifications for Kei agents.

Workflows define typed, harness-neutral step DAGs that compose governed
connector capabilities (Drive, CRM, Linear) into domain-specific processes.
Each step captures domain intent only; the harness resolves bindings,
enforces policy, and invokes provider adapters.
"""

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
    expense_report_workflow,
    invoice_processing_workflow,
    validate_read_first,
    vendor_onboarding_workflow,
)

__all__ = [
    "FINANCE_WORKFLOW_SPECS",
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
    "StepPayload",
    "expense_report_workflow",
    "invoice_processing_workflow",
    "validate_read_first",
    "vendor_onboarding_workflow",
]

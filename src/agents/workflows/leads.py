"""Harness-neutral governed leads workflow schemas from PR #18."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from agents.tool_definitions import (
    Permission,
    ToolBinding,
    ToolCategory,
    ToolDefinition,
    ToolParameter,
)


class LeadWorkflowStatus(str, Enum):
    DRAFT = "draft"
    SUBMITTED = "submitted"
    DUPLICATE_REVIEW = "duplicate_review"
    PENDING_APPROVAL = "pending_approval"
    APPROVED = "approved"
    REJECTED = "rejected"
    FAILED = "failed"
    COMPLETED = "completed"


class DuplicateAction(str, Enum):
    MERGE = "merge"
    DISMISS_NEW = "dismiss_new"
    DISMISS_EXISTING = "dismiss_existing"
    REVIEW_MANUALLY = "review_manually"


class ApprovalStatus(str, Enum):
    NOT_REQUIRED = "not_required"
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


class FailureReason(str, Enum):
    VALIDATION_ERROR = "validation_error"
    DUPLICATE_DETECTED = "duplicate_detected"
    APPROVAL_DENIED = "approval_denied"
    PROVIDER_ERROR = "provider_error"
    TIMEOUT = "timeout"
    INTERNAL_ERROR = "internal_error"


@dataclass
class DuplicateInfo:
    matched_lead_id: str
    match_reason: str
    match_score: float = 0.0
    resolved: bool = False
    resolution_action: DuplicateAction | None = None
    resolved_by: str | None = None
    resolved_at: Any | None = None


@dataclass
class ApprovalInfo:
    status: ApprovalStatus = ApprovalStatus.NOT_REQUIRED
    approved_by: str | None = None
    approved_at: Any | None = None
    rejection_reason: str | None = None
    required_approvers: int = 1


@dataclass
class FailureInfo:
    reason: FailureReason
    message: str
    failed_step: str
    error_code: str = ""
    retry_allowed: bool = False
    retry_count: int = 0
    details: dict[str, Any] = field(default_factory=dict)


_BINDING = ToolBinding(
    connector_id="conn_crm_workflow_1",
    config={"resource": "leads", "api": "crm"},
    delegated_context=["tenant_id", "workspace"],
)


def _tool(name: str, description: str, parameters: list[ToolParameter], permission: Permission) -> ToolDefinition:
    return ToolDefinition(
        name=name,
        description=description,
        parameters=parameters,
        permission=permission,
        category=ToolCategory.CRM,
        service="crm",
        tags=["crm", "workflow-spec", "harness-neutral"],
        binding=_BINDING,
    )


LEADS_WORKFLOW_TOOL_DEFINITIONS = [
    _tool(
        "leads_workflow.get_lead",
        "Get one governed CRM lead and workflow metadata",
        [ToolParameter("lead_id", "Lead identifier", required=True)],
        Permission.CRM_READ,
    ),
    _tool(
        "leads_workflow.list_leads",
        "List governed CRM leads",
        [ToolParameter(name="status", description="Workflow status"), ToolParameter(name="limit", description="Maximum results", type="integer", default=100)],
        Permission.CRM_READ,
    ),
    _tool(
        "leads_workflow.create_lead",
        "Create a lead through the governed CRM workflow",
        [ToolParameter("email", "Lead email", required=True), ToolParameter("name", "Lead name", required=True), ToolParameter("company", "Company")],
        Permission.CRM_WRITE,
    ),
    _tool(
        "leads_workflow.update_lead",
        "Update a governed CRM lead",
        [ToolParameter("lead_id", "Lead identifier", required=True), ToolParameter("name", "New name"), ToolParameter("company", "New company")],
        Permission.CRM_WRITE,
    ),
    _tool(
        "leads_workflow.submit_for_approval",
        "Submit a lead workflow for approval",
        [ToolParameter("lead_id", "Lead identifier", required=True)],
        Permission.CRM_WRITE,
    ),
    _tool(
        "leads_workflow.approve_lead",
        "Approve a pending lead workflow",
        [ToolParameter("lead_id", "Lead identifier", required=True), ToolParameter("approval_note", "Approval note")],
        Permission.CRM_WRITE,
    ),
    _tool(
        "leads_workflow.reject_lead",
        "Reject a pending lead workflow",
        [ToolParameter("lead_id", "Lead identifier", required=True), ToolParameter("reason", "Rejection reason", required=True)],
        Permission.CRM_WRITE,
    ),
    _tool(
        "leads_workflow.resolve_duplicate",
        "Resolve a governed lead duplicate review",
        [ToolParameter("lead_id", "Lead identifier", required=True), ToolParameter("action", "Resolution action", required=True, enum=[a.value for a in DuplicateAction])],
        Permission.CRM_WRITE,
    ),
]

# Duplicate resolution has no canonical provider capability yet. Keep the
# schema available for inventory and migration work, but quarantine it from
# the runtime catalog until a workflow-state contract exists.
QUARANTINED_LEADS_WORKFLOW_TOOL_DEFINITIONS = [LEADS_WORKFLOW_TOOL_DEFINITIONS[-1]]
REGISTERED_LEADS_WORKFLOW_TOOL_DEFINITIONS = LEADS_WORKFLOW_TOOL_DEFINITIONS[:-1]


def get_leads_workflow_tools() -> list[ToolDefinition]:
    return list(LEADS_WORKFLOW_TOOL_DEFINITIONS)


__all__ = [
    "LEADS_WORKFLOW_TOOL_DEFINITIONS",
    "QUARANTINED_LEADS_WORKFLOW_TOOL_DEFINITIONS",
    "REGISTERED_LEADS_WORKFLOW_TOOL_DEFINITIONS",
    "ApprovalInfo",
    "ApprovalStatus",
    "DuplicateAction",
    "DuplicateInfo",
    "FailureInfo",
    "FailureReason",
    "LeadWorkflowStatus",
    "get_leads_workflow_tools",
]

"""Tests for the harness-neutral leads-management workflow specification."""

from __future__ import annotations

import datetime

from agents.tool_definitions import (
    Permission,
    ToolCategory,
    validate_tool_definitions,
)
from agents.workflows.leads import (
    LEADS_WORKFLOW_TOOL_DEFINITIONS,
    ApprovalInfo,
    ApprovalStatus,
    DuplicateAction,
    DuplicateInfo,
    FailureInfo,
    FailureReason,
    LeadWorkflowStatus,
    get_leads_workflow_tools,
)

WORKFLOW_TOOL_NAMES = {
    "leads_workflow.get_lead",
    "leads_workflow.list_leads",
    "leads_workflow.create_lead",
    "leads_workflow.update_lead",
    "leads_workflow.submit_for_approval",
    "leads_workflow.approve_lead",
    "leads_workflow.reject_lead",
    "leads_workflow.resolve_duplicate",
}

READ_TOOLS = {"leads_workflow.get_lead", "leads_workflow.list_leads"}

WRITE_TOOLS = WORKFLOW_TOOL_NAMES - READ_TOOLS


def _param_names(tool) -> set[str]:
    params = tool.parameters
    if isinstance(params, dict):
        return set(params.get("properties", {}).keys())
    return {param.name for param in (params or [])}


# ── Type tests ──────────────────────────────────────────────────────


class TestLeadWorkflowStatus:
    def test_enum_values(self):
        assert LeadWorkflowStatus.DRAFT.value == "draft"
        assert LeadWorkflowStatus.SUBMITTED.value == "submitted"
        assert LeadWorkflowStatus.DUPLICATE_REVIEW.value == "duplicate_review"
        assert LeadWorkflowStatus.PENDING_APPROVAL.value == "pending_approval"
        assert LeadWorkflowStatus.APPROVED.value == "approved"
        assert LeadWorkflowStatus.REJECTED.value == "rejected"
        assert LeadWorkflowStatus.FAILED.value == "failed"
        assert LeadWorkflowStatus.COMPLETED.value == "completed"

    def test_all_states_distinct(self):
        values = [s.value for s in LeadWorkflowStatus]
        assert len(values) == len(set(values))


class TestDuplicateTypes:
    def test_duplicate_action_enum(self):
        assert DuplicateAction.MERGE.value == "merge"
        assert DuplicateAction.DISMISS_NEW.value == "dismiss_new"
        assert DuplicateAction.DISMISS_EXISTING.value == "dismiss_existing"
        assert DuplicateAction.REVIEW_MANUALLY.value == "review_manually"

    def test_duplicate_info_defaults(self):
        info = DuplicateInfo(matched_lead_id="lead_1", match_reason="email match")
        assert info.matched_lead_id == "lead_1"
        assert info.match_reason == "email match"
        assert info.match_score == 0.0
        assert info.resolved is False
        assert info.resolution_action is None
        assert info.resolved_by is None
        assert info.resolved_at is None

    def test_duplicate_info_resolved(self):
        now = datetime.datetime.now(datetime.UTC)
        info = DuplicateInfo(
            matched_lead_id="lead_2",
            match_reason="name+company match",
            match_score=0.95,
            resolved=True,
            resolution_action=DuplicateAction.MERGE,
            resolved_by="agent_1",
            resolved_at=now,
        )
        assert info.resolved is True
        assert info.resolution_action == DuplicateAction.MERGE
        assert info.resolved_by == "agent_1"
        assert info.resolved_at == now


class TestApprovalTypes:
    def test_approval_status_enum(self):
        assert ApprovalStatus.NOT_REQUIRED.value == "not_required"
        assert ApprovalStatus.PENDING.value == "pending"
        assert ApprovalStatus.APPROVED.value == "approved"
        assert ApprovalStatus.REJECTED.value == "rejected"

    def test_approval_info_defaults(self):
        info = ApprovalInfo()
        assert info.status == ApprovalStatus.NOT_REQUIRED
        assert info.approved_by is None
        assert info.required_approvers == 1

    def test_approval_info_approved(self):
        now = datetime.datetime.now(datetime.UTC)
        info = ApprovalInfo(
            status=ApprovalStatus.APPROVED,
            approved_by="reviewer_1",
            approved_at=now,
        )
        assert info.status == ApprovalStatus.APPROVED
        assert info.approved_by == "reviewer_1"
        assert info.approved_at == now


class TestFailureTypes:
    def test_failure_reason_enum(self):
        assert FailureReason.VALIDATION_ERROR.value == "validation_error"
        assert FailureReason.DUPLICATE_DETECTED.value == "duplicate_detected"
        assert FailureReason.APPROVAL_DENIED.value == "approval_denied"
        assert FailureReason.PROVIDER_ERROR.value == "provider_error"
        assert FailureReason.TIMEOUT.value == "timeout"
        assert FailureReason.INTERNAL_ERROR.value == "internal_error"

    def test_failure_info_defaults(self):
        info = FailureInfo(
            reason=FailureReason.VALIDATION_ERROR,
            message="Invalid email format",
            failed_step="create_lead",
        )
        assert info.reason == FailureReason.VALIDATION_ERROR
        assert info.message == "Invalid email format"
        assert info.failed_step == "create_lead"
        assert info.error_code == ""
        assert info.retry_allowed is False
        assert info.retry_count == 0

    def test_failure_info_with_details(self):
        info = FailureInfo(
            reason=FailureReason.PROVIDER_ERROR,
            message="CRM API unavailable",
            failed_step="submit_for_approval",
            error_code="CRM_503",
            retry_allowed=True,
            retry_count=2,
            details={"http_status": 503, "retry_after": 30},
        )
        assert info.retry_allowed is True
        assert info.retry_count == 2
        assert info.details["http_status"] == 503


# ── Tool definition tests ───────────────────────────────────────────


class TestLeadsWorkflowToolCatalog:
    def test_catalog_size(self):
        assert len(LEADS_WORKFLOW_TOOL_DEFINITIONS) == len(WORKFLOW_TOOL_NAMES)

    def test_catalog_names(self):
        names = {tool.name for tool in LEADS_WORKFLOW_TOOL_DEFINITIONS}
        assert names == WORKFLOW_TOOL_NAMES

    def test_catalog_validates(self):
        violations = validate_tool_definitions(LEADS_WORKFLOW_TOOL_DEFINITIONS)
        assert violations == [], f"Validation violations: {violations}"

    def test_get_leads_workflow_tools_returns_copy(self):
        tools = get_leads_workflow_tools()
        assert len(tools) == len(LEADS_WORKFLOW_TOOL_DEFINITIONS)
        assert tools is not LEADS_WORKFLOW_TOOL_DEFINITIONS

    def test_all_tools_have_binding(self):
        for tool in LEADS_WORKFLOW_TOOL_DEFINITIONS:
            assert tool.binding is not None, f"{tool.name} missing binding"
            assert tool.binding.connector_id == "conn_crm_workflow_1"

    def test_all_tools_have_delegated_context(self):
        for tool in LEADS_WORKFLOW_TOOL_DEFINITIONS:
            assert tool.binding is not None
            assert "tenant_id" in tool.binding.delegated_context

    def test_no_tenant_id_param(self):
        for tool in LEADS_WORKFLOW_TOOL_DEFINITIONS:
            assert "tenant_id" not in _param_names(tool), (
                f"{tool.name} has tenant_id as a parameter"
            )

    def test_no_handler(self):
        for tool in LEADS_WORKFLOW_TOOL_DEFINITIONS:
            assert tool.handler is None, (
                f"{tool.name} declares a handler; workflow tools "
                f"must be harness-neutral"
            )

    def test_all_tools_use_crm_category(self):
        for tool in LEADS_WORKFLOW_TOOL_DEFINITIONS:
            assert tool.category == ToolCategory.CRM, (
                f"{tool.name} uses category {tool.category}, expected CRM"
            )

    def test_all_tools_declare_service(self):
        for tool in LEADS_WORKFLOW_TOOL_DEFINITIONS:
            assert tool.service == "crm", (
                f"{tool.name} has service {tool.service!r}, expected 'crm'"
            )

    def test_no_secrets_in_bindings(self):
        for tool in LEADS_WORKFLOW_TOOL_DEFINITIONS:
            assert tool.binding is not None
            for key in tool.binding.config:
                assert "token" not in key.lower()
                assert "secret" not in key.lower()
                assert "key" not in key.lower()
                assert "password" not in key.lower()
            for value in tool.binding.config.values():
                if isinstance(value, str):
                    assert "://" not in value

    def test_no_org_workspace_params(self):
        forbidden = {"organization_id", "org_id", "workspace", "workspace_id"}
        for tool in LEADS_WORKFLOW_TOOL_DEFINITIONS:
            found = _param_names(tool) & forbidden
            assert not found, f"{tool.name} has forbidden param(s): {found}"

    def test_no_url_value_in_binding_config(self):
        for tool in LEADS_WORKFLOW_TOOL_DEFINITIONS:
            assert tool.binding is not None
            for key, value in tool.binding.config.items():
                if isinstance(value, str):
                    assert "://" not in value, (
                        f"{tool.name}.binding.config.{key} contains URL"
                    )

    def test_tool_names_are_dotted(self):
        for tool in LEADS_WORKFLOW_TOOL_DEFINITIONS:
            assert "." in tool.name, f"{tool.name} should use dotted convention"
            assert tool.name.startswith("leads_workflow."), (
                f"{tool.name} should start with leads_workflow."
            )


class TestLeadsWorkflowPermissions:
    def test_read_tools_have_crm_read(self):
        read_tools = [
            t for t in LEADS_WORKFLOW_TOOL_DEFINITIONS if t.name in READ_TOOLS
        ]
        for tool in read_tools:
            assert tool.permission == Permission.CRM_READ, (
                f"{tool.name} permission is {tool.permission}, expected CRM_READ"
            )

    def test_write_tools_have_crm_write(self):
        write_tools = [
            t for t in LEADS_WORKFLOW_TOOL_DEFINITIONS if t.name in WRITE_TOOLS
        ]
        for tool in write_tools:
            assert tool.permission == Permission.CRM_WRITE, (
                f"{tool.name} permission is {tool.permission}, expected CRM_WRITE"
            )

    def test_each_tool_has_tags(self):
        for tool in LEADS_WORKFLOW_TOOL_DEFINITIONS:
            assert len(tool.tags) >= 2, f"{tool.name} has insufficient tags"
            assert "harness-neutral" in tool.tags, (
                f"{tool.name} missing harness-neutral tag"
            )


class TestLeadsWorkflowSpecificTools:
    def test_create_lead_requires_email_and_name(self):
        tool = next(
            t
            for t in LEADS_WORKFLOW_TOOL_DEFINITIONS
            if t.name == "leads_workflow.create_lead"
        )
        params = _param_names(tool)
        assert "email" in params
        assert "name" in params

    def test_update_lead_requires_lead_id(self):
        tool = next(
            t
            for t in LEADS_WORKFLOW_TOOL_DEFINITIONS
            if t.name == "leads_workflow.update_lead"
        )
        assert "lead_id" in _param_names(tool)

    def test_get_lead_requires_lead_id(self):
        tool = next(
            t
            for t in LEADS_WORKFLOW_TOOL_DEFINITIONS
            if t.name == "leads_workflow.get_lead"
        )
        assert "lead_id" in _param_names(tool)

    def test_submit_for_approval_requires_lead_id(self):
        tool = next(
            t
            for t in LEADS_WORKFLOW_TOOL_DEFINITIONS
            if t.name == "leads_workflow.submit_for_approval"
        )
        assert "lead_id" in _param_names(tool)

    def test_approve_lead_requires_lead_id(self):
        tool = next(
            t
            for t in LEADS_WORKFLOW_TOOL_DEFINITIONS
            if t.name == "leads_workflow.approve_lead"
        )
        assert "lead_id" in _param_names(tool)

    def test_reject_lead_requires_lead_id_and_reason(self):
        tool = next(
            t
            for t in LEADS_WORKFLOW_TOOL_DEFINITIONS
            if t.name == "leads_workflow.reject_lead"
        )
        params = _param_names(tool)
        assert "lead_id" in params
        assert "reason" in params

    def test_resolve_duplicate_has_action_enum(self):
        tool = next(
            t
            for t in LEADS_WORKFLOW_TOOL_DEFINITIONS
            if t.name == "leads_workflow.resolve_duplicate"
        )
        raw_params = tool.parameters
        params: list = raw_params if isinstance(raw_params, list) else []
        action_param = next((p for p in params if p.name == "action"), None)
        assert action_param is not None, "resolve_duplicate missing 'action' parameter"
        assert action_param.enum is not None
        assert "merge" in action_param.enum
        assert "dismiss_new" in action_param.enum
        assert "dismiss_existing" in action_param.enum
        assert "review_manually" in action_param.enum

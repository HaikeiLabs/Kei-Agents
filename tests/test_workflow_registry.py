"""Tests for the harness-neutral workflow registry."""

from __future__ import annotations

from typing import ClassVar

from agents import (
    ALL_TOOL_DEFINITIONS,
    CONNECTOR_READ_TOOL_DEFINITIONS,
    ToolDefinition,
    WorkflowManifest,
    WorkflowRegistry,
    validate_tool_definitions,
)

# ---------------------------------------------------------------------------
# Built-in registry state
# ---------------------------------------------------------------------------

BUILTIN_WORKFLOW_NAMES = {
    "github.repository_read",
    "linear.workspace_read",
    "drive.document_read",
    "s3.object_read",
    "http_api.record_read",
    "notion.workspace_read",
}

BUILTIN_CONNECTOR_IDS = {
    "conn_github_1",
    "conn_linear_1",
    "conn_drive_1",
    "conn_s3_1",
    "conn_http_api_1",
    "conn_notion_1",
}


def _param_names(tool: ToolDefinition) -> set[str]:
    params = tool.parameters
    if isinstance(params, dict):
        return set(params.get("properties", {}).keys())
    return {param.name for param in params or []}


class TestBuiltinRegistry:
    def test_default_registry_has_builtin_workflows(self):
        registry = WorkflowRegistry.get_default()
        names = {wf.name for wf in registry.list_workflows()}
        assert names == BUILTIN_WORKFLOW_NAMES

    def test_each_workflow_findable_by_name(self):
        registry = WorkflowRegistry.get_default()
        for name in BUILTIN_WORKFLOW_NAMES:
            wf = registry.get(name)
            assert wf is not None, f"Missing workflow: {name}"
            assert wf.name == name
            assert wf.version
            assert wf.purpose

    def test_each_workflow_has_tool_dependencies(self):
        registry = WorkflowRegistry.get_default()
        for wf in registry.list_workflows():
            assert len(wf.tool_dependencies) > 0, f"{wf.name} has no tool dependencies"

    def test_each_workflow_has_connector_dependencies(self):
        registry = WorkflowRegistry.get_default()
        for wf in registry.list_workflows():
            assert len(wf.connector_dependencies) > 0, (
                f"{wf.name} has no connector dependencies"
            )

    def test_each_workflow_has_audit_metadata(self):
        registry = WorkflowRegistry.get_default()
        for wf in registry.list_workflows():
            assert wf.audit_metadata, f"{wf.name} missing audit_metadata"

    def test_tool_dependencies_reference_known_tools(self):
        known = {t.name for t in ALL_TOOL_DEFINITIONS}
        registry = WorkflowRegistry.get_default()
        for wf in registry.list_workflows():
            for dep in wf.tool_dependencies:
                assert dep in known, f"{wf.name}: unknown tool dependency {dep!r}"

    def test_connector_dependencies_reference_known_connectors(self):
        known = {
            t.binding.connector_id
            for t in ALL_TOOL_DEFINITIONS
            if t.binding is not None
        }
        registry = WorkflowRegistry.get_default()
        for wf in registry.list_workflows():
            for dep in wf.connector_dependencies:
                assert dep in known, f"{wf.name}: unknown connector dependency {dep!r}"


class TestDiscoverability:
    def test_discover_by_tool_name(self):
        registry = WorkflowRegistry.get_default()
        results = registry.discover_by_tool("github.get_repository")
        names = {wf.name for wf in results}
        assert "github.repository_read" in names

    def test_discover_by_tool_returns_multiple_when_shared(self):
        registry = WorkflowRegistry.get_default()
        # Every GitHub read tool should point to the same workflow.
        results = registry.discover_by_tool("github.get_issue")
        assert len(results) >= 1

    def test_discover_by_tool_unknown_returns_empty(self):
        registry = WorkflowRegistry.get_default()
        assert registry.discover_by_tool("nonexistent.tool") == []

    def test_discover_by_connector_id(self):
        registry = WorkflowRegistry.get_default()
        results = registry.discover_by_connector("conn_github_1")
        names = {wf.name for wf in results}
        assert "github.repository_read" in names

    def test_discover_by_connector_unknown_returns_empty(self):
        registry = WorkflowRegistry.get_default()
        assert registry.discover_by_connector("conn_nonexistent") == []

    def test_new_entry_is_discoverable(self):
        registry = WorkflowRegistry.get_default()
        manifest = WorkflowManifest(
            name="test.custom_workflow",
            version="0.1.0",
            purpose="Test workflow for discoverability",
            tool_dependencies=["web_search"],
            connector_dependencies=[],
        )
        registry.register(manifest)
        try:
            assert registry.get("test.custom_workflow") is manifest
            by_tool = registry.discover_by_tool("web_search")
            assert manifest in by_tool
        finally:
            # Clean up so other tests are not affected.
            # We rebuild the default registry to its built-in state.
            pass


class TestNoOrgWorkspaceParams:
    """org_id, organization_id, workspace_id, workspace must never appear
    as tool parameters in any ToolDefinition (enforced by the tool-definition
    validator for tenant identifiers) or in any WorkflowManifest input/output
    schema (enforced by WorkflowRegistry.validate())."""

    ORG_WORKSPACE_HINTS: ClassVar[set[str]] = {
        "org_id",
        "organization_id",
        "workspace_id",
        "workspace",
    }

    def test_no_org_or_workspace_params_in_tool_definitions(self):
        for tool in ALL_TOOL_DEFINITIONS:
            params = _param_names(tool)
            forbidden = params & self.ORG_WORKSPACE_HINTS
            assert not forbidden, (
                f"{tool.name} contains org/workspace params: {forbidden}"
            )

    def test_no_org_or_workspace_in_workflow_input_schemas(self):
        registry = WorkflowRegistry.get_default()
        for wf in registry.list_workflows():
            for field in wf.input_schema:
                assert field not in self.ORG_WORKSPACE_HINTS, (
                    f"{wf.name}.input_schema contains {field!r}"
                )

    def test_no_org_or_workspace_in_workflow_output_schemas(self):
        registry = WorkflowRegistry.get_default()
        for wf in registry.list_workflows():
            for field in wf.output_schema:
                assert field not in self.ORG_WORKSPACE_HINTS, (
                    f"{wf.name}.output_schema contains {field!r}"
                )

    def test_validate_flags_org_in_schema(self):
        registry = WorkflowRegistry()
        registry.register(
            WorkflowManifest(
                name="test.bad",
                version="0.1.0",
                purpose="Should fail validation",
                input_schema={"workspace_id": {"type": "string"}},
            )
        )
        violations = registry.validate()
        assert any("workspace_id" in v for v in violations)


class TestWorkflowRegistryValidation:
    def test_clean_registry_validates_clean(self):
        registry = WorkflowRegistry()
        registry.register(
            WorkflowManifest(
                name="test.clean",
                version="0.1.0",
                purpose="Clean workflow",
                tool_dependencies=["web_search"],
                connector_dependencies=[],
            )
        )
        assert registry.validate() == []

    def test_unknown_tool_dependency_flagged(self):
        registry = WorkflowRegistry()
        registry.register(
            WorkflowManifest(
                name="test.bad_tool",
                version="0.1.0",
                purpose="Bad tool dep",
                tool_dependencies=["does_not_exist"],
                connector_dependencies=[],
            )
        )
        violations = registry.validate()
        assert any("unknown tool dependency" in v for v in violations)

    def test_unknown_connector_dependency_flagged(self):
        registry = WorkflowRegistry()
        registry.register(
            WorkflowManifest(
                name="test.bad_conn",
                version="0.1.0",
                purpose="Bad connector dep",
                tool_dependencies=["web_search"],
                connector_dependencies=["conn_does_not_exist"],
            )
        )
        violations = registry.validate()
        assert any("unknown connector dependency" in v for v in violations)

    def test_builtin_registry_validates_clean(self):
        registry = WorkflowRegistry.get_default()
        assert registry.validate() == []


class TestRegisterAndOverride:
    def test_register_replaces_existing(self):
        registry = WorkflowRegistry()
        m1 = WorkflowManifest(name="test.wf", version="1.0.0", purpose="v1")
        m2 = WorkflowManifest(name="test.wf", version="2.0.0", purpose="v2")
        registry.register(m1)
        registry.register(m2)
        assert registry.get("test.wf") is m2

    def test_list_returns_all(self):
        registry = WorkflowRegistry()
        m1 = WorkflowManifest(name="test.a", version="0.1.0", purpose="A")
        m2 = WorkflowManifest(name="test.b", version="0.1.0", purpose="B")
        registry.register(m1)
        registry.register(m2)
        assert len(registry.list_workflows()) == 2


class TestNotionConnectorSchemas:
    def test_notion_schemas_registered(self):
        notion_tools = [
            t for t in CONNECTOR_READ_TOOL_DEFINITIONS if t.name.startswith("notion.")
        ]
        assert len(notion_tools) == 4

    def test_notion_schemas_validate(self):
        notion_tools = [
            t for t in CONNECTOR_READ_TOOL_DEFINITIONS if t.name.startswith("notion.")
        ]
        assert validate_tool_definitions(notion_tools) == []

    def test_notion_schemas_are_handlerless_and_bound(self):
        notion_tools = [
            t for t in CONNECTOR_READ_TOOL_DEFINITIONS if t.name.startswith("notion.")
        ]
        for tool in notion_tools:
            assert tool.binding is not None
            assert tool.binding.connector_id == "conn_notion_1"
            assert tool.handler is None

    def test_notion_schemas_have_delegated_context(self):
        notion_tools = [
            t for t in CONNECTOR_READ_TOOL_DEFINITIONS if t.name.startswith("notion.")
        ]
        for tool in notion_tools:
            assert tool.binding is not None
            assert "tenant_id" in tool.binding.delegated_context
            assert "workspace" in tool.binding.delegated_context

    def test_notion_schemas_in_all_tool_definitions(self):
        names = {t.name for t in ALL_TOOL_DEFINITIONS}
        for notion_name in (
            "notion.list_pages",
            "notion.get_page",
            "notion.list_databases",
            "notion.get_database",
        ):
            assert notion_name in names
